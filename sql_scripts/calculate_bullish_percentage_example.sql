SET @stock = 'AAPL';
SET @periodstart = '2016-01-01 00:00:00';
SET @periodend = '2016-01-07 23:59:59';

select 
(
Select count(sentiment) from messages_w_sentiment_v2 
WHERE time BETWEEN @periodstart AND @periodend
and symbol=@stock
and sentiment='bullish'
)

/

(
Select count(sentiment) from messages_w_sentiment_v2 
WHERE time BETWEEN @periodstart AND @periodend
and symbol=@stock
)

as bullish_percentage