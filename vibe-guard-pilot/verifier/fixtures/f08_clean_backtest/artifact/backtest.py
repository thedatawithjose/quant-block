def signals(df):
    # signal uses yesterday's close vs the day before
    df["signal"] = (df["close"].shift(1) > df["close"].shift(2)).astype(int)
    return df
