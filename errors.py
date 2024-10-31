class BadRequest(Exception):
    """Вызывается если приходит ошибка 400, обозначающая невалидные значения в query"""
    pass


class APIKeyError(Exception):
    """Вызывается если приходит ошибка 401, связанная с авторизацией APIKey"""
    pass
