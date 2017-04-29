SET @total = (select count(*) from messages_w_sentiment_v2);

select ( select count(*) from messages_w_sentiment_v2 where experience = 'Professional' ) / @total as professionals,
( select count(*) from messages_w_sentiment_v2 where experience = 'Intermediate' ) / @total as intermediates,
( select count(*) from messages_w_sentiment_v2 where experience = 'Novice' ) / @total as novices,
( select count(*) from messages_w_sentiment_v2 where experience = '' ) / @total as none
