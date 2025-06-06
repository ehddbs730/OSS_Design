class Region:
    _regions = [
        {"id": 1, "name": "서울 강남구"},
        {"id": 2, "name": "부산 해운대구"},
        {"id": 3, "name": "대구 수성구"},
        {"id": 4, "name": "제주 제주시"},
        {"id": 5, "name": "인천 연수구"},
    ]

    @classmethod
    def get_all(cls):
        return cls._regions

    @classmethod
    def get_by_id(cls, id):
        return next((r for r in cls._regions if r["id"] == id), None)
