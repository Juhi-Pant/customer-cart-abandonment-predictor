import joblib
import pandas as pd

# Load model artifacts
model = joblib.load('cart_model.pkl')
scaler = joblib.load('scaler.pkl')
feature_names = joblib.load('feature_names.pkl')

def predict_cart_abandonment(session_data: dict):
    """
    Input: session_data as a dictionary of features
    Output: probability of cart abandonment (float)
    """
    # Align input with training feature order
    X_input = pd.DataFrame([session_data])[feature_names]
    
    # Scale
    X_scaled = scaler.transform(X_input)
    

    # Predict
    prob = model.predict_proba(X_scaled)[0][1]  # Probability of '1' = abandon
    return round(prob, 4)

# Example usage
if __name__ == "__main__":
    test_session = {
        'Is_Product_Details_viewed': 1,
        'No_Items_Added_InCart': 2,
        'Session_Activity_Count': 5,
        # add all remaining required features from feature_names
    }

    result = predict_cart_abandonment(test_session)
    print("🛒 Abandonment Probability:", result)
