create view v_daily_performance_financial as
select stock.id, product.id, stock.date_of_delivery as
date_of_production, stock.place_from, stock.place_to,
(stock.quantity_change*product.unit_price) as value_recorded,
stock.additional_value from stock, product where
stock.date_of_delivery is not null and stock.quantity_change > 0 and
product.id = stock.product_id and product.product_group in (2,3) and
stock.place_from in (1,2,3,4) order by stock.date_of_Delivery desc;


create view v_daily_sum_performance_financial as
select date_format(stock.date_of_delivery,'%Y%m%d') AS
id,stock.date_of_delivery AS
date_of_production, sum((stock.quantity_change * product.unit_price))
AS value_recorded_sum sum(stock.additional_value) as 
additional_value_sum from (stock join product) where
((stock.date_of_delivery is not null) and (stock.quantity_change > 0)
and (product.id = stock.product_id) and (product.product_group in
(2,3)) and (stock.place_from in (1,2,3,4))) group by
~(stock.date_of_delivery) order by stock.date_of_delivery desc;


create view v_daily_place_sum_performance_financial as
select
concat(date_format(stock.date_of_delivery,'%Y%m%d'),stock.place_from)
AS id,stock.date_of_delivery AS date_of_production,stock.place_from AS
place_from,sum((stock.quantity_change * product.unit_price)) AS
value_recorded_sum, sum(stock.additional_value) as
additional_value_sum from (stock join product) where
((stock.date_of_delivery is not null) and (stock.quantity_change > 0)
and (product.id = stock.product_id) and (product.product_group in
(2,3)) and (stock.place_from in (1,2,3,4))) group by
~(stock.date_of_delivery),stock.place_from order by
stock.date_of_delivery desc,stock.place_from;
