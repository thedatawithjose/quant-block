def signals(df):
    # signal = tomorrow's return sign
    df["signal"] = (df["close"].shift(-1) > df["close"]).astype(int)
    return df
