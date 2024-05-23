from django.shortcuts import render
from .models import Stock, HistoricalData
from .ml_model import train_model
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def stock_detail(request, symbol):
    stock = Stock.objects.get(symbol=symbol)
    historical_data = HistoricalData.objects.filter(stock=stock).order_by('date')

    # Train the model
    model, scaler = train_model(symbol)

    # Prepare data for prediction
    df = pd.DataFrame(list(historical_data.values('close_price')))
    last_60_days = df[-60:].values
    last_60_days_scaled = scaler.transform(last_60_days)

    X_test = []
    X_test.append(last_60_days_scaled)
    X_test = np.array(X_test)
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    # Predict the next day's closing price
    predicted_price = model.predict(X_test)
    predicted_price = scaler.inverse_transform(predicted_price)

    # Plot the data
    fig, ax = plt.subplots()
    historical_df = pd.DataFrame(list(historical_data.values()))
    historical_df['date'] = pd.to_datetime(historical_df['date'])
    ax.plot(historical_df['date'], historical_df['close_price'], label='Historical Prices')
    ax.set_title(f'{stock.name} Stock Prices')
    ax.set_xlabel('Date')
    ax.set_ylabel('Close Price')
    ax.legend()

    # Encode the plot to display in the template
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    image_base64 = base64.b64encode(image_png).decode('utf-8')

    context = {
        'stock': stock,
        'historical_data': historical_data,
        'predicted_price': predicted_price[0][0],
        'chart': image_base64,
    }
    return render(request, 'templates/stocks/stock_detail.html', context)
