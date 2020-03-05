from matplotlib import pyplot as plt
from matplotlib import dates as mpl_dates
from io import BytesIO

plt.style.use('seaborn')


def draw_time_series(kwargs):
    new_dict = {k: list(v.values())[0] for k, v in kwargs.items()}

    timestamp, currency = zip(*new_dict.items())

    dates = mpl_dates.datestr2num(timestamp)

    plt.plot_date(x=sorted(dates), y=currency, linestyle='solid')
    plt.tight_layout()

    date_format = mpl_dates.DateFormatter('%d, %b, %Y')

    plt.gcf().autofmt_xdate()

    plt.gca().xaxis.set_major_formatter(date_format)

    buf = BytesIO()

    plt.savefig(buf, format='png')
    plt.close()
    data = buf.getvalue()

    return data
