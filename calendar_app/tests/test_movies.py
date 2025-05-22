def test_movie_list_page(client):
    response = client.get('/movies/list')
    assert response.status_code == 200
    assert b"All Movies" in response.data