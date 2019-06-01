import sys
import time

from process import wn_analysis

argv = sys.argv
if len(argv) == 1:
    print(
        "将要执行获取WN变价代码，若想获取数据分析，请执行：\n"
        "python wn.py percent=20 price_diff=100 =50 seat_clean=1"
        "\npercent:获取升价多少百分比以上\n"
        "price_diff：获取涨价超过多少美元以上\n"
        "num_clean：是否去除每小时小于多少的数据，默认不清除\n"
        "seat_clean：是否排除座位不相同，1为排除，默认不排除\n"
    )
    time.sleep(5)
    print("正在执行WN变价数据获取，预计完成需要3个小时")
    wn_analysis.main()
else:
    percent, price_diff, num_clean, seat_clean = 20, 100, None, None
    for arg in argv[1:]:
        v_a = arg.split('=')
        if 'percent' == v_a[0]:
            percent = int(v_a[1])
        if 'price_diff' == v_a[0]:
            price_diff = int(v_a[1])
        if 'num_clean' == v_a[0]:
            num_clean = int(v_a[1])
        if 'seat_clean' == v_a[0]:
            seat_clean = int(v_a[1])

    wn_analysis.process(percent, price_diff, num_clean, seat_clean)
