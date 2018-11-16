import graphene
from django.core.paginator import Paginator
from django.db.models import Q
from graphql import ResolveInfo

from problem.constant import PER_PAGE_COUNT
from problem.models import Problem
from problem.type import ProblemType, ProblemListType


class Query(object):
    problem = graphene.Field(ProblemType, slug=graphene.String())
    problem_list = graphene.Field(ProblemListType, page=graphene.Int(), filter=graphene.String())
    problem_search = graphene.Field(ProblemListType, filter=graphene.String())

    def resolve_problem(self: None, info: ResolveInfo, slug):
        problem_list = Problem.objects.all()
        privileage = info.context.user.has_perm('problem.view')
        if not privileage:
            problem_list = problem_list.filter(disable=False)
        return problem_list.get(slug=slug)

    def resolve_problem_list(self: None, info: ResolveInfo, page: int, filter: str):
        problem_list = Problem.objects.all()
        privileage = info.context.user.has_perm('problem.view')
        if not privileage:
            problem_list = problem_list.filter(disable=False)
        if filter:
            problem_list = problem_list.filter(Q(pk__contains=filter) | Q(title__icontains=filter))
        paginator = Paginator(problem_list, PER_PAGE_COUNT)
        return ProblemListType(maxpage=paginator.num_pages, problem_list=paginator.get_page(page))

    def resolve_problem_search(self: None, info: ResolveInfo, filter: str):
        problem_list = Problem.objects.all()
        if not info.context.user.has_perm('problem.view_all'):
            problem_list = problem_list.filter(disable=False)
        if filter:
            problem_list = problem_list.filter(Q(pk__contains=filter) | Q(title__icontains=filter))
        return ProblemListType(maxpage=1, problem_list=problem_list[:5])
