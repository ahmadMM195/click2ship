import requests
import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime, cstr
import json
import base64
KARRIO_BASE_URL = "https://api.click2ship.net"

#KARRIO_BASE_URL = "https://noninterpretational-madelene-geminally.ngrok-free.dev"

def _get_settings():
    """Get Karrio Settings Doc"""
    return frappe.get_single("Karrio Settings")

def _save_tokens(access_token, refresh_token, expires_in=3600):
    """Save new tokens in settings"""
    settings = _get_settings()
    settings.access_token = access_token
    settings.refresh_token = refresh_token
    settings.token_expiry = now_datetime()
    settings.save(ignore_permissions=True)
    frappe.db.commit()

@frappe.whitelist()
def get_auth_token(username, password):
    """
    Get authentication token from Karrio API and save into Karrio Settings
    """
    url = f"{KARRIO_BASE_URL}/api/token"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    data = {
        "email": username,   # Karrio expects email field
        "password": password
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            tokens = response.json()   # { "access": "...", "refresh": "..." }

            # Save into Karrio Settings
            _save_tokens(tokens.get("access"), tokens.get("refresh"))
            return tokens
        else:
            frappe.throw(f"Karrio Authentication failed: {response.status_code} {response.text}")
            
    except requests.exceptions.RequestException as e:
        frappe.throw(f"Karrio Authentication request failed: {str(e)}")


def refresh_token(refresh_token):
    """
    Refresh access token using Karrio refresh token endpoint
    """
    url = f"{KARRIO_BASE_URL}/api/token/refresh"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    data = {
        "refresh": refresh_token
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()  # Expected: { "access": "new_token" }
        else:
            frappe.throw(f"Karrio Token refresh failed: {response.status_code} {response.text}")
            
    except requests.exceptions.RequestException as e:
        frappe.throw(f"Karrio Token refresh request failed: {str(e)}")


def _get_valid_token():
    """Ensure a valid access token (refresh if expired or fallback to re-authenticate)"""
    settings = _get_settings()

    # No token at all — get fresh
    if not settings.access_token:
        auth = get_auth_token(settings.username, settings.password)
        _save_tokens(auth["access"], auth["refresh"])
        return auth["access"]

    # Token expired — try to refresh
    if settings.token_expiry and get_datetime(settings.token_expiry) < now_datetime():
        try:
            refreshed = refresh_token(settings.refresh_token)
            _save_tokens(refreshed["access"], settings.refresh_token)
            return refreshed["access"]
        except Exception as e:
            # Refresh token invalid — fallback to full login
            auth = get_auth_token(settings.username, settings.password)
            _save_tokens(auth["access"], auth["refresh"])
            return auth["access"]

    # Token still valid
    return settings.access_token



@frappe.whitelist(allow_guest=True)
def rates():
    # -----------------------------------------------
    # STEP 1 — Parse incoming request
    # -----------------------------------------------
    try:
        raw_data = frappe.request.get_data(as_text=True)
        if not raw_data:
            return {
                "success": False,
                "error_type": "invalid_request",
                "message": "No quote input data received."
            }
        quote_input = json.loads(raw_data)

    except Exception as e:
        return {
            "success": False,
            "error_type": "json_parse_error",
            "message": f"Error parsing request data: {str(e)}"
        }

    # -----------------------------------------------
    # STEP 2 — Build payload (you can map quote_input later)
    # -----------------------------------------------
    '''payload = {
          "shipper": {
              "postal_code": "SW1A1AA",
              "country_code": "GB"
          },
         "recipient": {
             "postal_code": "4008",
              "country_code": "AU"
          },
          "shipper": {
             "address": {
                 "country_code": "PK"
             }
         },
         "recipient": {
             "address": {
                "country_code": quote_input.get("destinationCountry","GB")
             }
         },
         "parcels": [
             {
                 "weight": 2,
                 "width": 1,
                 "height": 1,
                 "length": 1,
                 "Length": float(quote_input.get("boxlength", 1)),
                 "Width": float(quote_input.get("boxwidth", 1)),
                 "Height": float(quote_input.get("boxheight", 1)),
                 "Weight": float(quote_input.get("boxweight", 1)), 
                 "weight_unit": "KG",
                 "dimension_unit": "CM",
                 "items": [
                  {
                         "Weight": float(quote_input.get("boxweight", 1)),  
                         "weight_unit": "KG",
                         "value_amount": 25.00,
                         "value_currency": "USD",
                        "origin_country": "GB",
                   },
                   {
                          "weight": 1,
                          "weight_unit": "KG",
                          "value_amount": 25.00,
                          "value_currency": "USD",
                          "origin_country": "GB",
                    },
                    {
                        "weight": 1,
                        "weight_unit": "KG",
                         "value_amount": 15.00,
                          "value_currency": "USD",
                         "origin_country": "GB",
                     }
                 ],
                 "reference_number": "INV-1001",
                 "options": {},
             }
         ],
         "services": [],
         "options": {
             "currency": "USD",
             "insurance": 10.00,
             "dangerous_good": False,
             "declared_value": 50.00,
         },
         "reference": "TEST-FEDEX-GB-US",
    }'''
    #route_type = quote_input.get("intdestinationCountry")
    #destination_country = quote_input.get("intdestinationCountry", 1)
    
    print("#############112233221111232111")
    print(quote_input)
    
    post_code  = "SW1A1AA"
    count_code = "GB"
    city_ = "London"
    state_code_ = ""
    
    if quote_input.get("route_type", "") == 'International':
        post_code  = "54000"
        count_code = "PK"
        city_       =  "Sialkot"
        state_code_  = ""
    print(post_code)
    print(count_code)
    print(state_code_)
    payload = {
        "shipper": {            
            "postal_code": post_code,
            "city": city_,
            "federal_tax_id": "",
            "state_tax_id": "",
            "person_name": "",
            "company_name": "",
            "country_code": count_code,
            "email": "",
            "phone_number": "",
            "state_code": state_code_,
            "residential": False,
            "street_number": "",
            "address_line1": "String",
            "address_line2": "",
            "validate_location": False
        },
        "recipient": {
            "postal_code": quote_input.get("destinationZipcode", "12345"),
            "city": quote_input.get("destinationTown", "New"),
            "federal_tax_id": "",
            "state_tax_id": "",
            "person_name": "",
            "company_name": "",
            "country_code": quote_input.get("destinationCountry",""),
            "email": "",
            "phone_number": "",
            "state_code": quote_input.get("state_code", ""),
            "residential": False,
            "street_number": "",
            "address_line1": "String",
            "address_line2": "",
            "validate_location": False
            
        },
        "parcels": [
            {
                "weight": float(quote_input.get("boxweight", 1)),
                "width": float(quote_input.get("boxwidth", 1)),
                "height": float(quote_input.get("boxheight", 1)),
                "length": float(quote_input.get("boxlength", 1)),
                "packaging_type": "",
                "package_preset": "",
                "description": "",
                "content": "",
                "is_document": False,
                "weight_unit": "KG",
                "dimension_unit": "CM",
                "items": [
                    {
                        "weight": float(quote_input.get("boxweight", 1)),
                        "weight_unit": "KG",
                        "title": "",
                        "description": "",
                        "quantity": 1,
                        "sku": "",
                        "hs_code": "",
                        "value_amount": 0,
                        "value_currency": "USD",
                        "origin_country": count_code,
                        "product_url": "https://click2ship.com",
                        "image_url": "https://click2ship.com/image.png",
                        "product_id": "PID",
                        "variant_id": "VAR",
                        "parent_id": "PAR",
                        "metadata": {
                            "property1": None,
                            "property2": None
                        }
                    }                
                ],
                "reference_number": "REF",
                "freight_class": "gen",
                "options": {}
            }
            
            
        ],
        "services": [],
        "options": {
             "currency": "USD"
         },
        "reference": "string",
        "carrier_ids": []
    }

    '''payload = {
        "shipper": {
            "address": {
                "country_code": quote_input.get("originCountry", "PK")
            }
        },
        "recipient": {
            "address": {
                "country_code": quote_input.get("destinationCountry", "GB")
            }
        },
        "parcels": [
            {
                "length": float(quote_input.get("boxlength", 1)),
                "width": float(quote_input.get("boxwidth", 1)),
                "height": float(quote_input.get("boxheight", 1)),
                "weight": float(quote_input.get("boxweight", 1)),
                "dimension_unit": "CM",
                "weight_unit": "KG",
                "items": [
                    {
                        "weight": float(quote_input.get("boxweight", 1)),
                        "weight_unit": "KG",
                        "value_amount": 25,
                        "value_currency": "USD",
                        "origin_country": quote_input.get("originCountry", "PK")
                    }
                ]
            }
        ],
        "options": {
            "currency": "USD",
            "insurance": 10,
            "declared_value": 50,
            "dangerous_good": False
        },
        "carrier_ids": ["fedex"],
       "reference": "TEST-FEDEX-GB-US",
    }'''
    # -----------------------------------------------
    # STEP 3 — Send request to Karrio
    # -----------------------------------------------
    
    print("#######Karrio payload############")
    print(payload)
    access_token = _get_valid_token()
    url = f"{KARRIO_BASE_URL}/v1/proxy/rates"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-test-mode": "true",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        # frappe.error_log(response.json())

    except requests.exceptions.RequestException as e:
        # Network error, timeout → return clean error
        return {
            "success": False,
            "error_type": "network_error",
            "message": f"Karrio API request failed: {str(e)}"
        }

    # -----------------------------------------------
    # STEP 4 — Handle HTTP responses
    # -----------------------------------------------
    if response.status_code in [200, 207]:
        data = response.json()
        print("\n\n-----------------------")
        print(data)
        print("-----------------------\n\n")


        # Log partial success warnings quietly
        if response.status_code == 207:
            frappe.log_error(
                title="Karrio API partial success",
                message=f"Warnings: {data.get('messages')}"
            )
        rates = data.get("rates", [])
        print("before", payload)

        for rate in rates:
            rate['payload'] = payload
        print("Added karrio_payload to rate:", payload)
        return {
            "success": True,
            "kario_payload": payload,
            "rates": rates,
            "messages": data.get("messages", [])
        }

    # Token expired → reset & retry
    if response.status_code == 401:
        settings = _get_settings()
        settings.access_token = None
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        return rates()

    # Karrio returns structured error JSON → return parsed error
    try:
        err = response.json()
    except:
        err = {"message": response.text}

    return {
        "success": False,
        "error_type": "carrier_error",
        "carrier": err.get("messages", [{}])[0].get("carrier_name", "unknown"),
        "carrier_code": err.get("messages", [{}])[0].get("code"),
        "message": err.get("messages", [{}])[0].get("message") or "Carrier service unavailable",
        "raw": err
    }

@frappe.whitelist(allow_guest=True)
def shipment():
    """
    Create a shipment booking with Karrio API
    """
    try:
        # Get the access token
        access_token = _get_valid_token()
        url = f"{KARRIO_BASE_URL}/v1/proxy/shipping"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-test-mode": "true"
        }

        # Get data from the request
        shipment_data = frappe.request.get_json()


        
        if (shipment_data.get("recipient",{})).get("state_code","") == "string":
            shipment_data["recipient"]["state_code"] = ""
        if (shipment_data.get("shipper",{})).get("state_code","") == "string":
            shipment_data["shipper"]["state_code"] = ""
        # shipment_data["recipient"]["state_code"] = "NY"
        # shipment_data["recipient"]["shipper"] = ""
        # shipment_data["recipient"]["return_address"] = ""


        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Afterrrrrrrrrrrrrr#!!!!!!!!!!!!!!!!!")
        print(shipment_data)



        
        response = requests.post(url, json=shipment_data, headers=headers, timeout=15)
    
        if response.status_code not in [200, 201]:
            frappe.throw(f"Shipment API Error {response.status_code}: {response.text}")

        # Parse the response JSON
        resp_json = response.json()


        doc_url = {}
        # Extract fields
        barcode = resp_json.get("Barcode", {})

        # Store into ERPNext Doctype
        doc = frappe.new_doc("Shipment Booking")

        doc.shipping_service_name   =  "Karrio"
        doc.shipment_barcode        =  resp_json.get("id", "")


        doc.receiver_name           = resp_json.get("recipient", {}).get("person_name")
        doc.receiver_country        = resp_json.get("recipient", {}).get("country_code")
        doc.receiver_city           = resp_json.get("recipient", {}).get("city")
        doc.receiver_state          = resp_json.get("recipient", {}).get("state_code")
        doc.receiver_address1       = resp_json.get("recipient", {}).get("address_line1")
        doc.receiver_address2       = resp_json.get("recipient", {}).get("address_line2")
        doc.receiver_postal_code    = resp_json.get("recipient", {}).get("postal_code")
        doc.receiver_email          = resp_json.get("recipient", {}).get("email")
        doc.receiver_phone_number   = resp_json.get("recipient", {}).get("phone_number")


        doc.shipper_name           = resp_json.get("shipper", {}).get("person_name")
        doc.country_code           = resp_json.get("shipper", {}).get("country_code")
        doc.shipper_city           = resp_json.get("shipper", {}).get("city")
        doc.shipper_state          = resp_json.get("shipper", {}).get("state_code")
        doc.shipper_address1       = resp_json.get("shipper", {}).get("address_line1")
        doc.shipper_address2       = resp_json.get("shipper", {}).get("address_line2")
        doc.shipper_postal_code    = resp_json.get("shipper", {}).get("postal_code")
        doc.shipper_email          = resp_json.get("shipper", {}).get("email")
        doc.shipper_phone_number   = resp_json.get("shipper", {}).get("phone_number")
        
        documents = resp_json.get("docs", {})
        resp_json.pop("docs")



        doc.response = json.dumps(resp_json, indent=2)

        # doc.shipment_barcode = barcode
        doc.user = frappe.session.user
        
        # items_table = resp_json.get("parcels", {}).get("items", [])
        for row in resp_json.get("parcels", []):
            for items in row.get("items", []):
                doc.append('items', {
                    'item_name': "Karrio",
                    # 'item_description': items.description,
                    'quantity': items.get("quantity"),
                    'item_value': items.get("value_amount"),
                    'item_hscode': items.get("hs_code"),
                    'item_currency': items.get("value_currency"),
                    'item_weight': items.get("weight")
                })
        
        doc.insert(ignore_permissions=True)
        
        

        
        # for doc_item in documents:
        for category in ("label", "invoice"):
            base64_data = documents.get(category, "")
            
            if not base64_data:
                continue
            file_name = ""
            field_name = ""
            
            if category == "label":
                file_name = f"Shipment_Label_{resp_json.get('id', '')}.pdf"
                field_name = "label"
            elif category == "invoice":
                file_name = f"Shipment_Invoice_{resp_json.get('id', '')}.pdf"
                field_name = "invoice"
            else:
                continue
                
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": file_name,
                "attached_to_name": doc.name,
                "attached_to_doctype": "Shipment Booking",
                "attached_to_field": field_name,
                "is_private": 1,
                "content": base64.b64decode(base64_data)  # ✅ CORRECT
            })
            
            file_doc.insert(ignore_permissions=True)
            if file_doc.name:
                frappe.db.set_value("Shipment Booking", doc.name, field_name, file_doc.file_url)
                doc_url[category] = file_doc.file_url

        return_data = {}
        return_data["shipment_details"] = {
            "shipment_id": doc.name,
            "barcode": barcode,
            "doc_url": doc_url
        }
        return return_data

    except requests.exceptions.RequestException as req_err:
        frappe.log_error(frappe.get_traceback(), "Karrio Shipment API Request Error")
        frappe.throw(f"Network error while contacting Karrio Shipment API: {str(req_err)}")

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Unexpected Error in Shipment Booking")
        frappe.throw(f"An unexpected error occurred during shipment booking: {str(e)}")
        

@frappe.whitelist(allow_guest=True)
def schedule_proxy_pickup():
    """
    Schedule pickup using Karrio Proxy Pickup API
    Based strictly on /success session_data structure
    """

    try:
        # ------------------------------------
        # 1️⃣ Auth & headers
        # ------------------------------------
        access_token = _get_valid_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-test-mode": "true"
        }

        # ------------------------------------
        # 2️⃣ Read session data
        # ------------------------------------
        session_key = frappe.session.sid
        session_data = frappe.cache().get_value(f"session_data:{session_key}") or {}

        data = session_data.get("data", {})
        print("Dataaaaaaaaaaaaaaaaaaaaaaaa")
        print(data)
        shipment_data = frappe.request.get_json()
        print("shipment_dataaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print(shipment_data)

        booking = data.get("booking")
        if not booking:
            frappe.throw("Booking payload not found in session.")

        shipper = booking.get("shipper")
        parcels = booking.get("parcels", [])

        if not shipper or not parcels:
            frappe.throw("Shipper or parcels missing in booking data.")

        # ------------------------------------
        # 3️⃣ Carrier name (VERY IMPORTANT)
        # ------------------------------------
        rates = booking.get("rates", [])
        if not rates:
            frappe.throw("Carrier rate information missing.")

        carrier_name = rates[0].get("carrier_name")
        if not carrier_name:
            frappe.throw("Carrier name missing for pickup.")

        # ------------------------------------
        # 4️⃣ Pickup date & timing
        # ------------------------------------
        pickup_date = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

        ready_time = "10:00"
        closing_time = "18:00"

        # ------------------------------------
        # 5️⃣ Build pickup payload (STRICT)
        # ------------------------------------
        pickup_payload = {
            "pickup_date": pickup_date,
            "address": {
                "postal_code": shipper.get("postal_code"),
                "city": shipper.get("city"),
                "federal_tax_id": shipper.get("federal_tax_id", ""),
                "state_tax_id": shipper.get("state_tax_id", ""),
                "person_name": shipper.get("person_name"),
                "company_name": shipper.get("company_name", "N/A"),
                "country_code": shipper.get("country_code"),
                "email": shipper.get("email"),
                "phone_number": shipper.get("phone_number"),
                "state_code": shipper.get("state_code", ""),
                "residential": shipper.get("residential", False),
                "street_number": shipper.get("street_number", ""),
                "address_line1": shipper.get("address_line1"),
                "address_line2": shipper.get("address_line2", ""),
                "validate_location": False
            },
            "parcels": parcels,
            "ready_time": ready_time,
            "closing_time": closing_time,
            "instruction": "Pickup scheduled via Click2Ship",
            "package_location": "Reception",
            "options": {}
        }

        # ------------------------------------
        # 6️⃣ Call Karrio Proxy Pickup API
        # ------------------------------------
        pickup_url = f"{KARRIO_BASE_URL}/v1/proxy/pickups/{carrier_name}"

        response = requests.post(
            pickup_url,
            json=pickup_payload,
            headers=headers,
            timeout=20
        )

        if response.status_code not in (200, 201):
            frappe.throw(
                f"Pickup API Error {response.status_code}: {response.text}"
            )

        pickup_response = response.json()

        # ------------------------------------
        # 7️⃣ Save pickup result back to session
        # ------------------------------------
        data["pickup_details"] = pickup_response
        session_data["data"] = data

        frappe.cache().set_value(
            f"session_data:{session_key}",
            session_data,
            expires_in_sec=3600
        )

        return {
            "status": "success",
            "pickup_details": pickup_response
        }

    except requests.exceptions.RequestException as e:
        frappe.log_error(frappe.get_traceback(), "Pickup API Network Error")
        frappe.throw(str(e))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Pickup Scheduling Error")
        frappe.throw(str(e))


@frappe.whitelist(allow_guest=True)
def proxy_tracking():
    """
    Track shipment using Karrio Proxy Tracking API
    """

    try:
        # ------------------------------------
        # 1️⃣ Auth
        # ------------------------------------
        access_token = _get_valid_token()

        url = f"{KARRIO_BASE_URL}/v1/proxy/tracking"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-test-mode": "true"
        }

        # ------------------------------------
        # 2️⃣ Read request payload
        # ------------------------------------
        req = frappe.request.get_json() or {}

        tracking_number = req.get("tracking_number")
        carrier_name = req.get("carrier_name")

        if not tracking_number:
            frappe.throw("Tracking number is required")

        if not carrier_name:
            frappe.throw("Carrier name is required")

        # ------------------------------------
        # 3️⃣ Build tracking payload (STRICT)
        # ------------------------------------
        payload = {
            "tracking_number": tracking_number,
            "carrier_name": carrier_name,
            "account_number": req.get("account_number"),
            "reference": req.get("reference"),
            "info": req.get("info", {}),
            "metadata": req.get("metadata", {})
        }

        # ------------------------------------
        # 4️⃣ Call Karrio API
        # ------------------------------------
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code not in (200, 201):
            frappe.throw(
                f"Tracking API Error {response.status_code}: {response.text}"
            )

        return {
            "status": "success",
            "tracking": response.json()
        }

    except requests.exceptions.RequestException as e:
        frappe.log_error(frappe.get_traceback(), "Karrio Tracking Network Error")
        frappe.throw(str(e))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Karrio Tracking Error")
        frappe.throw(str(e))
        
@frappe.whitelist(allow_guest=True)
def track_shipment_by_booking(tracking_number: str):
    """
    Track shipment using Shipment Booking record
    """

    if not tracking_number:
        frappe.throw("Tracking number is required")

    # -------------------------------------------------
    # 1️⃣ Get Shipment Booking
    # -------------------------------------------------
    booking = frappe.db.get_value(
        "Shipment Booking",
        {"tracking_number": tracking_number},
        ["carrier_id", "carrier_name", "tracking_number","shipping_service_name"],
        as_dict=True
    )

    if not booking:
        frappe.throw("No shipment found for this tracking number")
        
    if booking.shipping_service_name == "Karrio":
        carrier_id = booking.carrier_id or booking.carrier_name
        carrier_name = booking.carrier_name

        if not carrier_id:
            frappe.throw("Carrier not found for this shipment")

        # -------------------------------------------------
        # 2️⃣ Auth
        # -------------------------------------------------
        access_token = _get_valid_token()

        url = f"{KARRIO_BASE_URL}/v1/proxy/tracking"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-test-mode": "true"
        }

        # -------------------------------------------------
        # 3️⃣ Build payload
        # -------------------------------------------------
        payload = {
            "tracking_number": tracking_number,
            "carrier_name": carrier_name.lower(),
            "reference": f"ShipmentBooking:{tracking_number}",
            "info": {},
            "metadata": {
                "source": "Shipment Booking"
            }
        }
        print(payload)

        # -------------------------------------------------
        # 4️⃣ Call Karrio
        # -------------------------------------------------
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=15
        )
    elif booking.shipping_service_name == "Skynet Express":
        ## here write code for skynet express tracking api
        url = "https://api.postshipping.com/api2/tracks"
        
        headers = {
            "Content-Type": "application/json",
            "Token": "WS_PSTest"
        }
        
        params = {
            "ReferenceNumber": reference_number
        }

        response = requests.get(url, headers=headers, params=params, timeout=15)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Tracking API failed {response.status_code}: {response.text}"
            )
    
    elif booking.shipping_service_name == "Norsk" or shipment_booked_with == "Norsk":
        from click2ship_core.api.norsk_api import track_norsk_shipment
        return track_norsk_shipment(tracking_number)
    print("------------------")
    print(response.status_code)
    print(response.text)
    if response.status_code not in (200, 201):
        frappe.throw(
            f"Tracking API Error {response.status_code}: {response.text}"
        )

    return {
        "status": "success",
        "shipment": booking,
        "tracking": response.json()
    }

