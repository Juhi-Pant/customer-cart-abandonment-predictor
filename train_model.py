from flask import Flask, request, jsonify
import joblib
import pandas as pd
import sqlite3
from datetime import datetime

# Load model, scaler, and feature names
model = joblib.load('cart_model.pkl')
scaler = joblib.load('scaler.pkl')
feature_names = joblib.load('feature_names.pkl')

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_data = request.json
        print("RAW INPUT:", input_data)

        # Convert to DataFrame
        df = pd.DataFrame([input_data])

        # Map binary fields to one-hot encoded columns
        binary_mappings = {
            "Is_Product_Details_viewed": "Is_Product_Details_viewed_Yes",
            "Is_User_Logged_In": "Is_User_Logged_In_Yes"
        }

        for original, one_hot in binary_mappings.items():
            df[one_hot] = input_data.get(original, 0)

        df.drop(columns=binary_mappings.keys(), inplace=True, errors='ignore')

        # Align with feature names
        df = df.reindex(columns=feature_names, fill_value=0)

        print("DataFrame Before Scaling:")
        print(df)

        # Scale and predict
        scaled_input = scaler.transform(df)
        print("Scaled Input:", scaled_input)

        proba = model.predict_proba(scaled_input)[0][1]
        print("Predicted Probability:", proba)

        # Log to SQLite
        try:
            conn = sqlite3.connect("abandonment_logs.db")
            cursor = conn.cursor()

            cursor.execute('''CREATE TABLE IF NOT EXISTS session_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                is_product_details_viewed INTEGER,
                no_items_added_incart INTEGER,
                session_activity_count INTEGER,
                no_of_product_clicks INTEGER,
                bounce_rate REAL,
                time_spent_on_site INTEGER,
                is_user_logged_in INTEGER,
                user_prior_abandonment_history INTEGER,
                prediction REAL,
                timestamp_logged TEXT
            )''')

            cursor.execute('''
                INSERT INTO session_logs (
                    user_id, is_product_details_viewed, no_items_added_incart,
                    session_activity_count, no_of_product_clicks, bounce_rate,
                    time_spent_on_site, is_user_logged_in, user_prior_abandonment_history,
                    prediction, timestamp_logged
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                input_data.get("user_id", None),
                input_data.get("Is_Product_Details_viewed", 0),
                input_data.get("No_Items_Added_InCart", 0),
                input_data.get("Session_Activity_Count", 0),
                input_data.get("No_of_Product_Clicks", 0),
                input_data.get("Bounce_Rate", 0.0),
                input_data.get("Time_Spent_on_Site", 0),
                input_data.get("Is_User_Logged_In", 0),
                input_data.get("User_Prior_Abandonment_History", 0),
                round(proba, 4),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()
            
        except Exception as db_error:
            print("SQLite Log Error:", db_error)

        return jsonify({
            "abandonment_probability": round(proba, 4)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "API is running"}), 200

if __name__ == '__main__':
    app.run(debug=True)
