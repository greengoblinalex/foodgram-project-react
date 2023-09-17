def get_is_subscribed(self, instance):
    # данный метод находится в 2х разных сериалайзерах,
    # поэтому, чтобы не нарушать принцип DRY,
    # я решил добавить его сюда
    user = self.context['request'].user
    if user.is_authenticated:
        return user.subscriptions.filter(pk=instance.pk).exists()
    return False
