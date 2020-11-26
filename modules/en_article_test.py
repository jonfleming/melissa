from .en_article import Article

def test(phrase):
    """
        Doc String
    """
    result = Article.getInstance().query(phrase)
    print(f"{result['article']} {phrase}" )


test("")
test("x")
test("\"x")
test("unanticipated result")
test("unanimous vote")
test("honest decision")
