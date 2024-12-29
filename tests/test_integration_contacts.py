from datetime import date, timedelta


def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json={
            "first_name": "Kate",
            "last_name": "Cake",
            "phone": "1987456321",
            "email": "kate@example.com",
            "birthday": "1998-10-01",
            "additional_info": "",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == "Kate"
    assert data["last_name"] == "Cake"
    assert data["phone"] == "1987456321"
    assert data["email"] == "kate@example.com"
    assert data["additional_info"] == ""
    assert "id" in data

def test_get_contacts(client, get_token):
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["first_name"] == "Alice"
    assert "id" in data[1]

def test_get_contact_by_id(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Alice"
    assert data["last_name"] == "Black"
    assert data["phone"] == "1999999999"
    assert data["email"] == "alice@example.com"
    assert data["birthday"] == str(date.today() + timedelta(days=5))
    assert data["additional_info"] == "Good friend"
    assert "id" in data

def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"

def test_update_contact(client, get_token):
    response = client.put(
        "/api/contacts/1",
        json={
            "first_name": "New Kate",
            "last_name": "SweetCake",
            "phone": "9632587412",
            "email": "sweetkate@example.com",
            "birthday": "1998-10-01",
            "additional_info": "!",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "New Kate"
    assert data["last_name"] == "SweetCake"
    assert data["phone"] == "9632587412"
    assert data["email"] == "sweetkate@example.com"
    assert data["additional_info"] == "!"
    assert "id" in data


def test_update_contact_not_found(client, get_token):
    response = client.put(
        "/api/contacts/999",
        json={
            "first_name": "New Kate",
            "last_name": "SweetCake",
            "phone": "9632587412",
            "email": "sweetkate@example.com",
            "birthday": "1998-10-01",
            "additional_info": "!",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Kate"
    assert "id" in data


def test_delete_nonexistent_contact(client, get_token):
    response = client.delete(
        "/api/contacts/999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"