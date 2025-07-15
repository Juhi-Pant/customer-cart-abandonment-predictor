CREATE TABLE session_logs (
    id SERIAL PRIMARY KEY,
    user_id INT,
    is_product_details_viewed BOOLEAN,
    no_items_added_incart INT,
    session_activity_count INT,
    no_of_product_clicks INT,
    bounce_rate FLOAT,
    time_spent_on_site FLOAT,
    is_user_logged_in BOOLEAN,
    user_prior_abandonment_history INT,
    prediction FLOAT,
    timestamp_logged TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
