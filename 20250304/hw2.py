def gcd(a, b):
    # 基本情況：當 b 等於 0 時，gcd 就是 a
    if b == 0:
        return a
    else:
        # 遞迴情況：計算 b 和 a 除以 b 的餘數的 gcd
        return gcd(b, a % b)
print(gcd(11, 121))
print(gcd(7, 49))                                                                                                                                                                                                                                                               