def test_create_and_list_movie(client):
    res = client.post("/movies", json={"title": "테스트 영화"})
    assert res.status_code == 201
    movie = res.json()
    assert movie["title"] == "테스트 영화"

    res = client.get("/movies")
    assert res.status_code == 200
    assert res.json() == [movie]


def test_create_movie_rejects_empty_title(client):
    assert client.post("/movies", json={"title": ""}).status_code == 422


def test_list_movies_limit_is_capped(client):
    assert client.get("/movies?limit=1001").status_code == 422
