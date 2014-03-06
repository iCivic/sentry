from sentry.api.serializers import Serializer, register
from sentry.constants import MEMBER_OWNER
from sentry.models import Team


@register(Team)
class TeamSerializer(Serializer):
    def attach_metadata(self, objects, user):
        team_list = Team.objects.get_for_user(user)
        for team in objects:
            try:
                team.access_type = team_list.get(team.slug).access_type
            except KeyError:
                team.access_type = None

    def serialize(self, obj, user):
        d = {
            'id': str(obj.id),
            'slug': obj.slug,
            'name': obj.name,
            'dateCreated': obj.date_added,
            'permission': {
                'edit': obj.access_type == MEMBER_OWNER,
            }
        }
        return d
