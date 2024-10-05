from sqlalchemy import select

from senpaisearch.models import User


def test_create_user(session):
    user = User(username='bogea', email='bogea@gmail.com', password='bogea123')
    session.add(user)
    session.commit()
    result = session.scalar(
        select(User).where(User.email == 'bogea@gmail.com')
    )

    assert result.username == 'bogea'
