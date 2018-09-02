from backtester.orderPlacer.base_order_placer import BaseOrderPlacer, PlacedOrder
from backtester.constants import *
import numpy as np


class Problem3OrderPlacer(BaseOrderPlacer):

    def __init__(self):
        self.__orders = []

    def mimicPriceOfConfirmation(self, instrument, timeOfExecution, timeOfConfirmation, instrumentsManager):
        tsParams = instrumentsManager.getTsParams()
        instrumentLookbackFeatures = instrumentsManager.getLookbackInstrumentFeatures()
        priceAtExecution = instrumentLookbackFeatures.getFeatureDf(tsParams.getPriceFeatureKey())[instrument.getInstrumentId()][-1]

        # priceAtExecution = instrument.getDataDf().iloc[-1][tsParams.getPriceFeatureKey()]
        # TODO: this price feature key should be present in book data
        priceAtConfirmation = instrument.getCurrentBookData()[tsParams.getPriceFeatureKey()]
        if ((timeOfConfirmation - timeOfExecution).seconds > 5):
            return priceAtExecution
        return priceAtConfirmation

    def getTradePriceAndPosition(self, instrument, price, spread, limit, position, instrumentsManager):
        instrumentLookbackFeatures = instrumentsManager.getLookbackInstrumentFeatures()
        bidPriceAtConfirmation = instrument.getCurrentBookData()['bidPrice']
        askPriceAtConfirmation = instrument.getCurrentBookData()['askPrice']
        lastTradePriceAtConfirmation = instrument.getCurrentBookData()['lastTradedPrice']
        lastTradeVolAtConfirmation = instrument.getCurrentBookData()['lastTradedVol']
        if (price is None)&(np.abs(position)!=0) :
            if np.sign(position) > 0:
                return [askPriceAtConfirmation, -position]
            elif np.sign(position) < 0:
                return [bidPriceAtConfirmation, -position]
            else:
                return [0,0]
        else:
            if lastTradePriceAtConfirmation <=price - spread/2:
                if (np.sign(position) < 0)&(np.abs(position)!=0) :
                    return [price - spread/2, -position]
                else:
                    return [price - spread/2,max(1,int(.01*lastTradeVolAtConfirmation))]
            elif lastTradePriceAtConfirmation >=price + spread/2:
                if (np.sign(position) >0)&(np.abs(position)!=0) :
                    return [price + spread/2, -position]
                else:
                    return [price + spread/2,-max(1,int(.01*lastTradeVolAtConfirmation))]
            else:
                return [price,0]


    def placeOrders(self, time, instrumentExecutions, instrumentsManager):
        for instrumentExecution in instrumentExecutions:
            instrumentId = instrumentExecution.getInstrumentId()
            factor = 1 if instrumentExecution.getExecutionType() == INSTRUMENT_EXECUTION_BUY else -1
            changeInPosition = instrumentExecution.getVolume() * factor
            placedOrder = PlacedOrder(instrumentId=instrumentId,
                                      changeInPosition=changeInPosition,
                                      timeOfExecution=instrumentExecution.getTimeOfExecution(),
                                      tradeLoss=0.0)
            if  hasattr(instrumentExecution, 'price'):
                setattr(placedOrder, 'price', instrumentExecution.price)
                setattr(placedOrder, 'spread', instrumentExecution.spread)
                setattr(placedOrder, 'limit', instrumentExecution.limit)
            self.__orders.append(placedOrder)

    def emitPlacedOrders(self, time, instrumentsManager):
        for placedOrder in self.__orders:
            instrumentId = placedOrder.getInstrumentId()
            instrument = instrumentsManager.getInstrument(instrumentId)
            if  hasattr(placedOrder, 'price'):
                price = placedOrder.price
                spread = placedOrder.spread
                limit = placedOrder.limit
            else:
                price = None
                spread = None
                limit = None

            [tradePrice, position]= self.getTradePriceAndPosition(instrument, price, spread, limit, placedOrder._PlacedOrder__changeInPosition, instrumentsManager)
            placedOrder.setTradePrice(tradePrice)
            placedOrder._PlacedOrder__changeInPosition = position
            yield(placedOrder)
        self.__orders = []
