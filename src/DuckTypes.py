import time, pandas as pd, numpy as np, warnings
from datetime import datetime, timedelta

from Valera import dbg

"""
Each class could be called upon to, given arg:
. retrive/create an instance
  or
. retrive/create class's main value
Both will run a check for whether the object meets criterions for being of the class.
The main value is always V
"""
class ClassTemplate:
    #* If anything needs to be callable from the outside, should start with a Capital letter
    def __new__(cls, value):
        if isinstance(value, cls):
            return value
        else:
            return super().__new__(cls)
    def __init__(self, value):
        self.V = self.__class__.Value(value)
        if isinstance(value, self.__class__):
            return None
        #* other needed values here
    @classmethod
    def Value(cls, value):
        if isinstance(value, cls):
            value = value.V
        #* assertions here
        return value

class Market:
    def __new__(cls, value):
        if isinstance(value, cls):
            return value
        else:
            return super().__new__(cls)
    def __init__(self, market):
        self.V = self.__class__.Value(market)
        if isinstance(market, self.__class__):
            return None
        self.BinanceBaseUrl = 'https://fapi.binance.com/fapi/v1' if self.V=='perp' else 'https://api.binance.com/api/v3'
    @classmethod
    def Value(cls, value):
        if isinstance(value, cls):
            value = value.V
        if value not in ['perp', 'spot']:
            raise ValueError("Valid options for market are 'perp' or 'spot'")
        return value
        
class USDTSymbol:
    def __new__(cls, value):
        if isinstance(value, cls):
            return value
        else:
            return super().__new__(cls)
    def __init__(self, symbol):
        self.V = self.__class__.Value(symbol)
        if isinstance(symbol, self.__class__):
            return None
        self.Coin = self.V[:-4].lower()
    @classmethod
    def Value(cls, value):
        if isinstance(value, cls):
            value = value.V
        if not value.isupper():
            raise ValueError(f"Provided symbol is of incorrect format: {value}")
        if not value.endswith('USDT'):
            raise ValueError(f"USDTSymbol must be quoted against USDT")
        return value
    
class BinanceTf:
    def __new__(cls, value):
        if isinstance(value, cls):
            return value
        else:
            return super().__new__(cls)
    def __init__(self, tf):
        self.V = self.__class__.Value(tf)
        if isinstance(tf, self.__class__):
            return None
        self.Seconds = self.__class__.getSeconds(self.V)
    @classmethod
    def Value(cls, value):
        if isinstance(value, cls):
            value = value.V
        if isinstance(value, int):
            value = cls.fromSeconds(value)
        if value not in ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']:
            raise ValueError(f"Invalid tf format. Received: {value}")
        return value
    def getSeconds(tf):
        num = int(tf[:-1])
        interval = tf[-1]
        map = {
            'm': 60,
            'h': 60*60,
            'd': 24*60*60,
            'w': 7*24*60*60,
            'M': 30*24*60*60
        }
        multiplier = map.get(interval)
        seconds = num*multiplier
        return seconds
    def fromSeconds(seconds):
        atLeastTf = None
        numerator = seconds        
        if numerator % 60 == 0:
            numerator /= 60
            atLeastTf = 'm'
        if numerator % 60 == 0:
            numerator /= 60
            atLeastTf = 'h'
        if numerator % 24 == 0:
            numerator /= 24
            atLeastTf = 'd'
        if numerator % 7 == 0:
            if numerator % 30 == 0:
                numerator /= 30
                atLeastTf = 'M'
            else:
                numerator /= 7
                atLeastTf = 'w'
        tf = f"{int(numerator)}{atLeastTf}"
        return tf
    
class Timestamp:
    def __new__(cls, value):
        if isinstance(value, cls):
            return value
        else:
            return super().__new__(cls)
    def __init__(self, timestamp):
        self.V = self.__class__.Value(timestamp)
        if isinstance(timestamp, self.__class__):
            return None
        self.Unix_ns = self.convertAnyToUnixNs(self.V)
        self.Unix_s = int(round(self.Unix_ns/1_000_000_000))
        self.Unix_ms = int(round(self.Unix_ns/1_000_000))
        self.Unix_us = int(round(self.Unix_ns/1_000))
        self.Datetime = datetime.fromtimestamp(self.Unix_ns/1_000_000_000)
        self.Isoformat = self.Datetime.isoformat()
    @classmethod
    def Value(cls, value):
        if isinstance(value, cls):
            value = value.V # returning the original Timestamp value, because there is no main value here
        return value
    def convertAnyToUnixNs(self, timestamp):
        unix_ns = None
        # checks if isoformat
        try:
            dt = datetime.fromisoformat(timestamp)
            unix_ns = dt.timestamp() * 1_000_000_000
        except:pass
        # checks if datetime
        try: unix_ns = timestamp.timestamp()*1_000_000_000
        except:pass
        # checks if unix
        try:
            if len(str(round(timestamp))) == 10:
                unix_ns = timestamp * 1_000_000_000
            if len(str(round(timestamp))) == 13:
                unix_ns = timestamp * 1_000_000
            if len(str(round(timestamp))) == 16:
                unix_ns = timestamp * 1_000
            if len(str(round(timestamp)))==19:
                unix_ns = timestamp
            assert 0 <= unix_ns/1_000_000_000 <= time.time()
        except:pass
            
        assert unix_ns != None, f"Provided timestamp type isn't supported.\nProvided: {timestamp}\nSupported: [unix_s, unix_ms, unix_us, unix_ns, datetime, isoformat], where only isoformat can be string"
        return unix_ns
    
class ClosesDf(ClassTemplate):
    def __init__(self, closesDf):
        self.V = self.__class__.Value(closesDf)
        if isinstance(closesDf, self.__class__):
            return None
    @classmethod
    def Value(cls, value):
        if isinstance(value, cls):
            value = value.V
        assert isinstance(value, pd.DataFrame)
        for column in value.columns:
            assert USDTSymbol(column)
        assert isinstance(value.index[0], datetime)
        assert np.any(value.iloc[:, 0].values == 0), f"Data does not go through 0.0, so assuming the df to be not normalized. Normalize the dataframe. Currently first column is: {value.iloc[:, 0].values}"
        return value
        
class Klines:
    def __new__(cls, value):
        if isinstance(value, cls):
            return value
        else:
            return super().__new__(cls)
    def __init__(self, klinesDf):
        self.V = self.__class__.Value(klinesDf)
        if isinstance(klinesDf, self.__class__):
            return None
        self.Market:Market = None
        try:self.Tf:BinanceTf = self.determineTf()
        except:self.Tf = None
        self.Full = None #* can be 'perp', 'spot' or None
        self.Normalized = False
        # if .Full != None, means we'll have additional columns, that consitute 'perp' Full or 'spot' Full
    @classmethod
    def Value(cls, value):
        if isinstance(value, cls):
            value = value.V
        assert isinstance(value, pd.DataFrame)
        assert isinstance(value.index[0], datetime)
        mandatoryColumns = ['open', 'high', 'low', 'close', 'volume']
        for column in mandatoryColumns:
            assert column in value.columns
        value[mandatoryColumns] = value[mandatoryColumns].apply(pd.to_numeric)
        return value
    def CollectFullData(self):
        raise 'Not Implemented Yet'
        assert (self.Market != None and self.Tf == None), "Klines object should have both self.Market and self.Tf specified for this function to be collable"
        _, _ = Market.Value(self.Market), BinanceTf.Value(self.Tf)
    def Normalize(self, dtTimestamp:Timestamp=None):
        if not self.Normalized:
            df = self.V
            zeroIndex = df.index[0] if dtTimestamp == None else Timestamp(dtTimestamp).datetime
            columns = ['open', 'high', 'low', 'close', 'oi', 'lsr']
            for column in columns:
                if column in df.columns:
                    zeroValue = df.loc[zeroIndex, column]
                    df[column] = df[column].apply(lambda x: round(np.log( x /zeroValue)*100, 3))
    def determineTf(self):
        secondIndexTimestamp = Timestamp(self.V.index[1])
        thirdIndexTimestamp = Timestamp(self.V.index[2])
        seconds = thirdIndexTimestamp.Unix_s - secondIndexTimestamp.Unix_s
        return BinanceTf(seconds).V
                
class SymbolsKlines:
    def __new__(cls, value):
        if isinstance(value, cls):
            return value
        else:
            return super().__new__(cls)
    def __init__(self, klinesDict):
        self.V = self.__class__.Value(klinesDict)
        if isinstance(klinesDict, self.__class__):
            return None
    @classmethod
    def Value(cls, value):
        if isinstance(value, cls):
            value = value.V
        assert isinstance(value, dict)
        assert len(value) >= 1
        for symbol, df in value.items():
            _, _ = USDTSymbol(symbol), Klines(df)
        return value
    def Normalize(self, dtTimestamp:Timestamp=None):
        for symbol, k in self.V.items():
            k.Normalize(dtTimestamp)
    def ToOpensDf(self) -> ClosesDf:
        self.Normalize()
        NormalizedKlinesDict = self.V
        opensDf = pd.DataFrame({symbol: k.V['close'] for symbol, k in NormalizedKlinesDict.items()})
        return opensDf