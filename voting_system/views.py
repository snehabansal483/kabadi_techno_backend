from rest_framework.views import APIView
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from .models import Voters, Votes
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

class PostVote(APIView):
    serializer_class = PostVoteSerializer
    def post(self, request):
        serializer = PostVoteSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            vote_id = request.data['vote']
            ip_add = request.data['ip']
            # if Voters.objects.filter(ip = ip_add).exists():
            try:
                voter = Voters.objects.get(ip = ip_add)
                return Response({'unsuccessful': 'You have already Voted', 'Your Voting Choice was : ': voter.status, 'ip address': voter.ip})
            # else:
            except:
                status = request.data['status']
                voter = Voters.objects.create(ip = ip_add, status = status, vote_id = vote_id)
                # serializer.save()
                vote = Votes.objects.get(id = vote_id)
                if status == 'Yes':
                    vote.yes_count += 1
                elif status == 'No':
                    vote.no_count += 1
                vote.save()
                return Response({'successful': 'Your Vote has been registered', 'Your Voting Choice is : ': voter.status,})

class GetVotes(APIView):
    def get(self, request, votes_id):
        votes_id = votes_id
        try:
            voting_title = Votes.objects.get(id = votes_id)
            serializer = GetVotesSerializer(voting_title)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'Non-Existence': 'There are no votes for this voting id'}, status=status.HTTP_204_NO_CONTENT)
