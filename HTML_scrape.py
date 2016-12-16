from bs4 import BeautifulSoup
from selenium import webdriver
from flask import Flask
import datetime

app = Flask(__name__)
app.logger.setLevel(10)
app.last_fetch = datetime.datetime.now()


def html_scrape():
    # phantom pretends to be a browser in order to use info given
    driver = webdriver.PhantomJS()
    # open page to scrape
    driver.get('https://www.redditgifts.com/gallery/#/?type=exchanges'
               '&pageNumber=1&pageSize=21&sort=date&sortDirection=DESC')
    # parse it
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # get each title out
    each_title = []
    titles = soup.select('.gallery-item__title')
    for t in titles:
        each_title.append(t.text.strip())
    # get each image out
    each_image = []
    images = soup.select('.gallery-item__image')
    for i in images:
        each_image.append(i['style'][22:-3])
    # get each link out
    each_link = []
    for l in titles:
        each_link.append('https://www.redditgifts.com' + l['href'].strip())
    # get each amount of upvotes
    each_upvote = []
    upvotes = soup.select('.gallery-item__info__vote__number')
    for u in upvotes:
        each_upvote.append(u.text)
    # return list of tuples
    return list(zip(each_upvote, each_title, each_link, each_image))


# create table rows
def show_datum(datum):
    return '''<div class="col-lg-4 col-md-4 col-sm-4 col-xs-4">
                <div><a href="{}">{}</a></div>
                <div><img src="{}"></div>
                <div>[Upvotes: {}]</div>
              </div>
'''.format(datum[2], datum[1], datum[3], datum[0])


# create html and table
def show_html(data):
    # rows = ''.join(show_datum(d) for d in range(len(data)))
    rows = [data[i:i + 3] for i in range(0, len(data), 3)]
    rows = ''.join(
        '<div class="row">{}</div>'.format(''.join(show_datum(d) for d in row))
        for row in rows)
    return '''
<html>
    <head>
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
rel="stylesheet"
integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u"
crossorigin="anonymous">
        <link rel="stylesheet" type="text/css" href="/static/scrapecss.css" />
    </head>
    <body>
        <div class="container-fluid">
            <div class="col-lg-offset-1 col-md-offset-1 col-sm-offset-1 col-xs-offset-1 col-lg-10 col-md-10 col-sm-10 col-xs-10">
                <div>Reddit Gifts</div>
                <div>{rows}</div>
                <div>{timestamp}</div>
            </div>
        </div>
    </body>
</html>
'''.format(rows=rows,
           timestamp=app.last_fetch.strftime('%I:%M:%S %p on %A, %B %d, %Y'))


app.data = html_scrape()


@app.route('/')
def root():
    # only refresh if it has been 3 or more minutes since last scrape
    if datetime.datetime.now() - app.last_fetch > datetime.timedelta(
            minutes=3):
        app.data = html_scrape()
        app.last_fetch = datetime.datetime.now()
    html = show_html(app.data)
    return html


if __name__ == '__main__':
    app.run()
