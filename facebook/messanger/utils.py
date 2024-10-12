import base64

def generate_private_room_name(user1_id, user2_id):
   
    room_name = f"private_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"
    room_name_encoded = base64.urlsafe_b64encode(room_name.encode()).decode()
    return room_name_encoded

def decode_private_room_name(encoded_room_name):
    room_name = base64.urlsafe_b64decode(encoded_room_name.encode()).decode()
    return room_name