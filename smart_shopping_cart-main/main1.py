import streamlit as st
from ultralytics import YOLO
from PIL import Image
import requests
from io import BytesIO
import pandas as pd
import time

# Constants
IMAGE_URL = "http://172.20.10.4:81"  # Replace with your dynamic image URL
MODEL_PATH = "own_data.pt"
REFRESH_INTERVAL = 3  # Time in seconds
PRICES = {  # Add your price mapping here
    "amrutanjan": 48,
    "aqua_lens_cleaner": 150,
    "ayush_jaggery_powder": 60,
    "Bourbon_biscuit": 25,
    "custard_powder": 40,
    "dettol_cool_max": 70,
    "dove_soap": 80,
    "dove_soap_pack_3": 155,
    "Dru_tablets": 390,
    "Eucalyptus_oil": 45,
    "fevi_stick": 50,
    "fogg_deodrant": 225,
    "good_night_liquid": 90,
    "gopuram_turmeric_powder": 25,
    "Iodex": 170,
    "KS_deodrant": 370,
    "lion_honey": 270,
    "maggi_noodles": 14,
    "mdh_garam_masala": 105,
    "Milk_Biscuit": 35,
    "moms_magic_biscuit": 35,
    "mtr_bisebelebath_powder": 155,
    "mtr_hing": 47,
    "mtr_vangibath_powder": 80,
    "neosprin": 132,
    "Nice_biscuit": 25,
    "oreo_biscuit": 30,
    "parachute_oil": 10,
    "pepsodent_complete_care": 140,
    "Ponds-S_Talcum_Powder": 380,
    "surf_excel_liquid": 102,
    "Vaseline": 50,
    "Vicks_vapour_Rub": 170,
    "vivel_alovera_soap": 60,
    "vanish": 78,
}


# Initialize YOLO model
model = YOLO(MODEL_PATH)

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "home"

if "items" not in st.session_state:
    st.session_state.items = []

if "total_amount" not in st.session_state:
    st.session_state.total_amount = 0

# Function to fetch and process the image
def fetch_and_process_image():
    try:
        # Fetch the image from the URL
        response = requests.get(IMAGE_URL, timeout=2)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))

        # Perform object detection
        results = model.predict(source=image, conf=0.40, iou=0.50, verbose=False)

        # Display the image
        image_placeholder.image(image, caption="Fetched Image", width=600)

        # Process results and update state
        items = []
        for result in results:
            for box in result.boxes:
                label_index = int(box.cls)
                label_name = result.names[label_index]
                price = PRICES.get(label_name, 0)

                # Add or update item
                existing_item = next((item for item in items if item["ITEM NAME"] == label_name), None)
                if existing_item:
                    existing_item["QUANTITY"] += 1
                    existing_item["AMOUNT"] += price
                else:
                    items.append({"ITEM NAME": label_name, "QUANTITY": 1, "AMOUNT": price})

        # Update detected items and total amount
        st.session_state.items = items
        st.session_state.total_amount = sum(item["AMOUNT"] for item in items)

        # Display the table
        if items:
            total_row = {"ITEM NAME": "Total", "QUANTITY": "", "AMOUNT": st.session_state.total_amount}
            items_with_total = items + [total_row]
            df = pd.DataFrame(items_with_total)
            table_placeholder.table(df)
        else:
            table_placeholder.warning("No objects detected.")
    except requests.exceptions.RequestException as e:
        table_placeholder.error(f"Error fetching image: {e}")
    except Exception as e:
        table_placeholder.error(f"An error occurred: {e}")

# Home page - Object Detection & Billing
if st.session_state.page == "home":
    st.title("YOLO Object Detection App")
    st.write("Automatically fetch and process images from a changing URL every few seconds.")

    # Placeholders for dynamic updates
    image_placeholder = st.empty()
    table_placeholder = st.empty()

    # Fetch and process the image
    fetch_and_process_image()

    # "Pay Now" button
    if st.button("Pay Now", key="pay_now_button"):
        st.session_state.page = "payment"
        st.rerun()

    # Delay for the refresh interval
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

# Payment page
elif st.session_state.page == "payment":
    st.title("Payment Page")
    st.write("Enter your payment details to complete the transaction.")

    # Payment form
    card_number = st.text_input("Card Number", key="card_number_input")
    expiry_date = st.text_input("Expiry Date (MM/YY)", key="expiry_date_input")
    cvv = st.text_input("CVV", type="password", key="cvv_input")

    st.write(f"Total Amount: ₹{st.session_state.total_amount}")

    if st.button("Confirm Payment", key="confirm_payment_button"):
        st.success("Payment Successful! Thank you for shopping.")
        # Reset state
        st.session_state.page = "home"
        st.session_state.items = []
        st.session_state.total_amount = 0

    if st.button("Back to Cart", key="back_to_cart_button"):
        st.session_state.page = "home"
