from backtester.trading_system_parameters import TradingSystemParameters
from backtester.features.feature import Feature
from datetime import timedelta
from backtester.dataSource.csv_data_source import CsvDataSource
from backtester.timeRule.nse_time_rule import NSETimeRule
from problem4_execution_system import Problem4ExecutionSystem
from backtester.orderPlacer.backtesting_order_placer import BacktestingOrderPlacer
from backtester.trading_system import TradingSystem
from backtester.version import updateCheck
from backtester.constants import *
from backtester.features.feature import Feature
from backtester.logger import *
import pandas as pd
import numpy as np
import sys
from sklearn import linear_model
from sklearn import metrics as sm

## Make your changes to the functions below.
## SPECIFY the symbols you are modeling for in getSymbolsToTrade() below
## You need to specify features you want to use in getInstrumentFeatureConfigDicts() and getMarketFeatureConfigDicts()
## and create your predictions using these features in getPrediction()

## Don't change any other function
## The toolbox does the rest for you, from downloading and loading data to running backtest


class MyTradingParams(TradingSystemParameters):
    '''
    initialize class
    place any global variables here
    '''
    def __init__(self, tradingFunctions):
        self.__tradingFunctions = tradingFunctions
        self.__dataSetId = self.__tradingFunctions.getDataSetId()
        self.__instrumentIds = self.__tradingFunctions.getSymbolsToTrade()
        self.__priceKey = 'F5'
        self.__additionalInstrumentFeatureConfigDicts = []
        self.__additionalMarketFeatureConfigDicts = []
        self.__fees = {'brokerage': 0.0001,'spread': 0.05}
        self.__startDate = '2010/06/02'
        self.__endDate = '2013/02/07'
        super(MyTradingParams, self).__init__()


    '''
    Returns an instance of class DataParser. Source of data for instruments
    '''

    def getDataParser(self):
        instrumentIds = self.__tradingFunctions.getSymbolsToTrade()
        return CsvDataSource(cachedFolderName='historicalData/',
                             dataSetId=self.__dataSetId,
                             instrumentIds=instrumentIds,
                             downloadUrl = 'https://raw.githubusercontent.com/Auquan/qq5Data/master',
                             timeKey = 'datetime',
                             timeStringFormat = '%Y-%m-%d %H:%M:%S',
                             startDateStr=self.__startDate,
                             endDateStr=self.__endDate,
                             liveUpdates=True,
                             pad=True)

    '''
    Returns an instance of class TimeRule, which describes the times at which
    we should update all the features and try to execute any trades based on
    execution logic.
    For eg, for intra day data, you might have a system, where you get data
    from exchange at a very fast rate (ie multiple times every second). However,
    you might want to run your logic of computing features or running your execution
    system, only at some fixed intervals (like once every 5 seconds). This depends on your
    strategy whether its a high, medium, low frequency trading strategy. Also, performance
    is another concern. if your execution system and features computation are taking
    a lot of time, you realistically wont be able to keep upto pace.
    '''
    def getTimeRuleForUpdates(self):
        return NSETimeRule(startDate=self.__startDate, endDate=self.__endDate, frequency='M', sample='30')

    '''
    Returns a timedetla object to indicate frequency of updates to features
    Any updates within this frequncy to instruments do not trigger feature updates.
    Consequently any trading decisions that need to take place happen with the same
    frequency
    '''

    def getFrequencyOfFeatureUpdates(self):
        return timedelta(60, 0)  # minutes, seconds

    def getStartingCapital(self):
        return 20000000#*len(self.__instrumentIds)

    '''
    This is a way to use any custom features you might have made.
    Returns a dictionary where
    key: featureId to access this feature (Make sure this doesnt conflict with any of the pre defined feature Ids)
    value: Your custom Class which computes this feature. The class should be an instance of Feature
    Eg. if your custom class is MyCustomFeature, and you want to access this via featureId='my_custom_feature',
    you will import that class, and return this function as {'my_custom_feature': MyCustomFeature}
    '''

    def getCustomFeatures(self):
        customFeatures = {'prediction': TrainingPredictionFeature,
                'fees_and_spread': FeesCalculator,
                'benchmark_PnL': BuyHoldPnL,
                'ScoreCalculator' : ScoreCalculator}
        customFeatures.update(self.__tradingFunctions.getCustomFeatures())


        return customFeatures


    def getInstrumentFeatureConfigDicts(self):
        # ADD RELEVANT FEATURES HERE

        predictionDict = {'featureKey': 'prediction',
                                'featureId': 'prediction',
                                 'params': {'function': self.__tradingFunctions}}
        feesConfigDict = {'featureKey': 'fees',
                          'featureId': 'fees_and_spread',
                          'params': {'feeDict': self.__fees,
                                    'price': self.getPriceFeatureKey(),
                                    'position' : 'position'}}
        profitlossConfigDict = {'featureKey': 'pnl',
                                'featureId': 'pnl',
                                'params': {'price': self.getPriceFeatureKey(),
                                           'fees': 'fees'}}
        capitalConfigDict = {'featureKey': 'capital',
                             'featureId': 'capital',
                             'params': {'price': self.getPriceFeatureKey(),
                                        'fees': 'fees',
                                        'capitalReqPercent': 0.95}}
        benchmarkDict = {'featureKey': 'benchmark',
                     'featureId': 'benchmark_PnL',
                     'params': {'pnlKey': 'pnl',
                                'price': self.getPriceFeatureKey()}}

        scoreDict = {'featureKey': 'score',
                     'featureId': 'ScoreCalculator',
                     'params': {'predictionKey': 'prediction',
                                'targetVariable' : self.__tradingFunctions.getTargetVariableKey(),
                                'price': self.getPriceFeatureKey()}}


        stockFeatureConfigs = self.__tradingFunctions.getInstrumentFeatureConfigDicts()


        return {INSTRUMENT_TYPE_STOCK: stockFeatureConfigs + [predictionDict,
                feesConfigDict,profitlossConfigDict,capitalConfigDict,benchmarkDict, scoreDict]
                + self.__additionalInstrumentFeatureConfigDicts}

    '''
    Returns an array of market feature config dictionaries
        market feature config Dictionary has the following keys:
        featureId: a string representing the type of feature you want to use
        featureKey: a string representing the key you will use to access the value of this feature.this
        params: A dictionary with which contains other optional params if needed by the feature
    '''

    def getMarketFeatureConfigDicts(self):
    # ADD RELEVANT FEATURES HERE
        scoreDict = {'featureKey': 'score',
                     'featureId': 'score_ll',
                     'params': {'featureName': self.getPriceFeatureKey(),
                                'instrument_score_feature': 'score'}}

        marketFeatureConfigs = self.__tradingFunctions.getMarketFeatureConfigDicts()
        return marketFeatureConfigs + [scoreDict] +self.__additionalMarketFeatureConfigDicts

    '''
    Returns the type of execution system we want to use. Its an implementation of the class ExecutionSystem
    It converts prediction to intended positions for different instruments.
    '''

    def getExecutionSystem(self):
        return Problem4ExecutionSystem(enter_threshold=0.99,
                                    exit_threshold=0.55,
                                    longLimit=10000,
                                    shortLimit=10000,
                                    capitalUsageLimit=0.10 * self.getStartingCapital(),
                                    enterlotSize=1, exitlotSize = 1,
                                    limitType='L', price=self.getPriceFeatureKey())

    '''
    Returns the type of order placer we want to use. its an implementation of the class OrderPlacer.
    It helps place an order, and also read confirmations of orders being placed.
    For Backtesting, you can just use the BacktestingOrderPlacer, which places the order which you want, and automatically confirms it too.
    '''

    def getOrderPlacer(self):
        return BacktestingOrderPlacer()

    '''
    Returns the amount of lookback data you want for your calculations. The historical market features and instrument features are only
    stored upto this amount.
    This number is the number of times we have updated our features.
    '''

    def getLookbackSize(self):
        return max(720, self.__tradingFunctions.getLookbackSize())

    def getPriceFeatureKey(self):
        return self.__priceKey

    def setPriceFeatureKey(self, priceKey='Adj_Close'):
        self.__priceKey = priceKey

    def getDataSetId(self):
        return self.__dataSetId

    def setDataSetId(self, dataSetId):
        self.__dataSetId = dataSetId

    def getInstrumentsIds(self):
        return self.__instrumentIds

    def setInstrumentsIds(self, instrumentIds):
        self.__instrumentIds = instrumentIds

    def getDates(self):
        return {'startDate':self.__startDate,
                'endDate':self.__endDate}

    def setDates(self, dateDict):
        self.__startDate = dateDict['startDate']
        self.__endDate = dateDict['endDate']

    def setFees(self, feeDict={'brokerage': 0.0001,'spread': 0.05}):
        self.__fees = feeDict

    def setAdditionalInstrumentFeatureConfigDicts(self, dicts = []):
        self.__additionalInstrumentFeatureConfigDicts = dicts

    def setAdditionalMarketFeatureConfigDicts(self, dicts = []):
        self.__additionalMarketFeatureConfigDicts = dicts

class TrainingPredictionFeature(Feature):

    @classmethod
    def computeForInstrument(cls, updateNum, time, featureParams, featureKey, instrumentManager):
        tf = featureParams['function']
        predictions = pd.Series(0.5, index = instrumentManager.getAllInstrumentsByInstrumentId())
        predictions = tf.getPrediction(time, updateNum, instrumentManager, predictions)
        if (predictions!= 1).any() & (predictions[predictions!= 1]!= 0).any() & (predictions[(predictions!= 1)&(predictions!=0)]!= 0.5).any():
            logError('Predictions can only take values 0/1/0.5' +
                    '\n' + 'Code will exit!!!')
            print(predictions)
            print((predictions!= 1).any())
            print((predictions!= 0).any())
            print((predictions!= 0.5).any())
            sys.exit(1)
        return predictions

class FeesCalculator(Feature):

    @classmethod
    def computeForInstrument(cls, updateNum, time, featureParams, featureKey, instrumentManager):
        instrumentLookbackData = instrumentManager.getLookbackInstrumentFeatures()

        priceData = instrumentLookbackData.getFeatureDf(featureParams['price'])
        positionData = instrumentLookbackData.getFeatureDf(featureParams['position'])
        currentPosition = positionData.iloc[-1]
        previousPosition = 0 if updateNum < 2 else positionData.iloc[-2]
        changeInPosition = currentPosition - previousPosition
        fees = pd.Series(np.abs(changeInPosition)*featureParams['feeDict']['brokerage'],index = instrumentManager.getAllInstrumentsByInstrumentId())
        if len(priceData)>1:
            currentPrice = priceData.iloc[-1]
        else:
            currentPrice = 0

        fees = fees*currentPrice + np.abs(changeInPosition)*featureParams['feeDict']['spread']

        return fees


class BuyHoldPnL(Feature):
    @classmethod
    def computeForInstrument(cls, updateNum, time, featureParams, featureKey, instrumentManager):
        instrumentLookbackData = instrumentManager.getLookbackInstrumentFeatures()

        priceData = instrumentLookbackData.getFeatureDf(featureParams['price'])
        bhpnl = pd.Series(0,index = instrumentManager.getAllInstrumentsByInstrumentId())
        if len(priceData)>1:
            bhpnl += priceData.iloc[-1] - priceData.iloc[-2]

        return bhpnl

class ScoreCalculator(Feature):
    @classmethod
    def computeForInstrument(cls, updateNum, time, featureParams, featureKey, instrumentManager):
        instrumentLookbackData = instrumentManager.getLookbackInstrumentFeatures()

        predictionData = instrumentLookbackData.getFeatureDf(featureParams['predictionKey']).iloc[-1]
        trueValue = instrumentLookbackData.getFeatureDf(featureParams['targetVariable']).iloc[-1]
        if updateNum <2 :
            return pd.Series(0.5, index=predictionData.index)
        previousValue = instrumentLookbackData.getFeatureDf(featureKey).iloc[-1]
        currentScore = pd.Series(0.5, index=previousValue.index)
        currentScore[predictionData!=0.5] = currentScore +(0.5 -  np.abs(predictionData - trueValue))
        # printdf = pd.DataFrame(index=predictionData.index)
        # printdf['predictionData'] = predictionData
        # printdf['trueValue'] = trueValue
        # printdf['previousValue'] = previousValue
        # printdf['currentScore']=currentScore

        # print(printdf)
        score = (previousValue*(updateNum-1)+currentScore)/updateNum#sm.accuracy_score(predictionData, trueValue)
        return score
