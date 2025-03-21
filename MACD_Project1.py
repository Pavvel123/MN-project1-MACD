import pandas as pd
import matplotlib.pyplot as plt


def EMA(n: int, x: list[float]) -> list[float | None]:
    emaList: list[float | None] = []
    start = 0
    for i in range(0, len(x)):
        if x[i] is None:
            emaList.append(None)
            start += 1
        elif i == 0 or (i > 0 and emaList[i - 1] is None):
            emaList.append(x[i])
        else:
            alpha = 2 / (n + 1)
            emaList.append(alpha * x[i] + (1 - alpha) * emaList[i - 1])
    for i in range(start, start + n):
        emaList[i] = None
    return emaList


def MACD(data: list[float]) -> list[float | None]:
    ema12 = EMA(12, data)
    ema26 = EMA(26, data)
    macd_data = []
    for i in range(0, len(ema12)):
        if ema26[i] is None:
            macd_data.append(None)
        else:
            macd_data.append(ema12[i] - ema26[i])
    return macd_data


def SIGNAL(MACD_data: list[float | None]) -> list[float | None]:
    return EMA(9, MACD_data)


def buyAndSellPoints(macd: list[float | None], signal: list[float | None], dates) -> tuple:
    buyPointsDates = []
    buyPointsValues = []
    sellPointsDates = []
    sellPointsValues = []
    dates = pd.to_numeric(dates)
    for i in range(0, len(macd) - 1):
        if signal[i] is not None:
            dif1 = macd[i] - signal[i]
            dif2 = macd[i + 1] - signal[i + 1]

            if (dif1 > 0 > dif2) or (dif1 < 0 < dif2):
                a1 = (macd[i] - macd[i + 1]) / (dates[i] - dates[i + 1])
                b1 = macd[i] - (a1 * dates[i])

                a2 = (signal[i] - signal[i + 1]) / (dates[i] - dates[i + 1])
                b2 = signal[i] - (a2 * dates[i])

                x_temp = (b2 - b1) / (a1 - a2)

                if dif1 < 0:
                    buyPointsDates.append(x_temp)
                    buyPointsValues.append(a1 * x_temp + b1)
                else:
                    sellPointsDates.append(x_temp)
                    sellPointsValues.append(a1 * x_temp + b1)
    buyPointsDates = pd.to_datetime(buyPointsDates)
    sellPointsDates = pd.to_datetime(sellPointsDates)
    return buyPointsDates, buyPointsValues, sellPointsDates, sellPointsValues


def importData(path, separ='\t', reverse=True) -> tuple:
    data = pd.read_csv(path, sep=separ)
    if reverse:
        data = data[::-1]
        data.index = data.index[::-1]
    date = pd.to_datetime(data['Date'])
    price = data['Price']
    return date, price


def plotData(date, price, colour, title):
    plt.figure(figsize=(15, 7))
    plt.plot(date, price, colour)
    plt.grid()
    plt.title(title)
    plt.xlabel("date")
    plt.ylabel("price [USD]")
    plt.legend(["Asustek price"])
    plt.show()


def plotMACD(date, macd, macdColour, signal, signalColour, sellDates, sellValues, sellColour, buyDates, buyValues, buyColour):
    plt.figure(figsize=(15, 7))
    plt.plot(date, macd, macdColour)
    plt.plot(date, signal, signalColour)
    plt.plot(buyDates, buyValues, buyColour)
    plt.plot(sellDates, sellValues, sellColour)
    plt.axvline(x=date[26], color='k')
    plt.grid()
    plt.title("MACD")
    plt.xlabel("date")
    plt.ylabel("MACD and SIGNAL value")
    plt.legend(["MACD", "SIGNAL", "buy points", "sell points"])
    plt.show()


data_date, data_price = importData('ASUS_data.csv')
plotData(data_date, data_price, 'k', "Asustek Stock Price History")
MACD_data = MACD(data_price)
SIGNAL_data = SIGNAL(MACD_data)
buyDates, buyValues, sellDates, sellValues = buyAndSellPoints(MACD_data, SIGNAL_data, data_date)
plotMACD(data_date, MACD_data, 'c', SIGNAL_data, 'm', sellDates, sellValues, 'bv', buyDates, buyValues, 'r^')
