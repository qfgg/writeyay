import os
import re
import json
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .forms import EssayForm
from subscription.models import Subscription
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from openai import OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)


EXAMPLE = {
  "overall": {
    "total": 5.5,
    "breakdown": {
      "ta": 6,
      "cc": 5,
      "lr": 5,
      "gra": 5
    },
    "summary": {
      "ta": "The essay addresses both views regarding animal rights and exploitation but lacks detailed support for each view. The argument for each side is presented, but the response could benefit from more balanced examples and a clearer explanation of the writer’s opinion.",
      "cc": "The essay has a logical structure, but the flow between ideas is sometimes unclear. Transition sentences could be improved, and some paragraphs lack clear cohesion. The organization of the essay needs better clarity and linking.",
      "lr": "The essay uses a range of vocabulary, but there are several instances of inappropriate or incorrect word choices. Some words and phrases are used inaccurately or repetitively.",
      "gra": "The essay contains various grammatical errors and awkward sentence structures. There is a need for greater accuracy and complexity in sentence formation."
    }
  },
  "explanations": [
    {
      "bad": "a countless number of people that are showing interest in what concerne animals rights",
      "hint": "The phrase should be 'an increasing number of people who are showing interest in animal rights.' The use of 'a countless number' is incorrect, and 'concerne' should be 'concern.'"
    },
    {
      "bad": "animal’s abuse is punished with fees and occasionally with prison",
      "hint": "The correct form is 'animal abuse is punished with fines and sometimes imprisonment.' The possessive 'animal’s' is incorrect, and 'fees' should be 'fines.'"
    },
    {
      "bad": "animal breeding has been observed and people are realizing that the killing and the slaughter of animals is cruelly done",
      "hint": "A better way to phrase this is 'animal breeding is regulated, and people are recognizing that the killing and slaughter of animals can be cruel.' The current phrasing is awkward and unclear."
    },
    {
      "bad": "exstremist thought",
      "hint": "The correct term is 'extremist views.' 'Exstremist' is a misspelling, and 'thought' should be 'views' in this context."
    },
    {
      "bad": "vegeterian people",
      "hint": "The correct term is 'vegetarian people.' 'Vegeterian' is a misspelling."
    },
    {
      "bad": "directly demaging the research sector",
      "hint": "The correct phrase is 'directly damaging the research sector.' 'Demaging' is a misspelling."
    },
    {
      "bad": "animalists did not know that for each treatment was used anesthesia",
      "hint": "The correct sentence is 'animal rights activists did not know that anesthesia was used for each procedure.' The current phrasing is grammatically incorrect and unclear."
    },
    {
      "bad": "exetremist thought",
      "hint": "The correct term is 'extremist views.' 'Exetremist' is a misspelling."
    }
  ],
  "splits": [
    {
      "id": -1,
      "val": "In this century, there are ",
    },
    {
      "id": 0,
      "val": "a countless number of people that are showing interest in what concerne animals rights",
    },
    {
      "id": -1,
      "val": ", therefore it is becoming an actual and argued topic. People are starting to look disapprovingly all situations and events with animal exploitation.    Infact, circus for example, has lost its popularity and the audience prefer human performances. Moreover, animal rights have become part of the law and ",
    },
    {
      "id": 1,
      "val": "animal’s abuse is punished with fees and occasionally with prison",
    },
    {
      "id": -1,
      "val": ". Further more, also the ",
    },
    {
      "id": 2,
      "val": "animal breeding has been observed and people are realizing that the killing and the slaughter of animals is cruelly done",
    },
    {
      "id": -1,
      "val": ". It is important to realize that people of new generations are developing a new sensibility concerning this issue, but currently it is emerging a new ",
    },
    {
      "id": 3,
      "val": "exstremist thought",
    },
    {
      "id": -1,
      "val": ". Despite the huge number of ",
    },
    {
      "id": 4,
      "val": "vegeterian people",
    },
    {
      "id": -1,
      "val": " (which the majority of them are following a new fashion), there are also people with distorted views. The area that worry me most regards the animal research which allows considerable and important improvements in the medical research, therefore in  human walfare. The animalist group are spreading wrong information , ",
    },
    {
      "id": 5,
      "val": "directly demaging the research sector",
    },
    {
      "id": -1,
      "val": ". As an illustration, few months ago an animalist  group destroyed years and years of neurological research freeing  rats used in a laboratory, because they would have been cruelly treated.  Unfortunately this ",
    },
    {
      "id": 6,
      "val": "animalists did not know that for each treatment was used anesthesia",
    },
    {
      "id": -1,
      "val": ". Given these points, I defend animal rights and I do not support any form of animal exploitation , nevertheless I do not support any ",
    },
    {
      "id": 7,
      "val": "exetremist thought",
    },
    {
      "id": -1,
      "val": "  especially concerning medical research.",
    },
  ]
}

PROMPT='''You are a professional on IELTS writing. You will be given a topic and an essay, and you can only follow steps to evaluate this essay based on the IELTS band score standard. If the user gives something other than IELTS writing, return a JSON object: {error: please input an essay with a topic for evaluation}.
Step 1: get a JSON object overall = {total: total score, breakdown: {ta: Task Achievement score,cc: Coherence and Cohesion score,lr: Lexical Resource score,gra: Grammatical Range and Accuracy score}, summary: {ta: analysis of Task Achievement with examples,cc: analysis of Coherence and Cohesion with examples,lr: summary of Lexical Resource,gra: summary of Grammatical Range and Accuracy};
Step 2: Check all words and expressions in the essay from start to end and find as many improper usage as possible. For each case, get an example = {bad: improper word or expression from original essay, hint: explain why it’s improper and how to improve it}. After checking the whole essay, get an array examples = an array of all examples you found in order;
Step 3: return a JSON object: {overall: overall, explanations: explanations} from step 1 and 2.
'''

def chatCompletions(data):
  return client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {"role": "system", "content": PROMPT},
      {"role": "user", "content": data},
    ],
    response_format={ "type": "json_object" }
  )

def splitEssay(essay, bad_list):
  # 创建一个映射，将 bad 列表中的每个片段映射到其 ID
  bad_map = {bad: idx for idx, bad in enumerate(bad_list)}
  # 使用正则表达式构造一个模式，将所有 bad 片段作为分隔符
  # `re.escape` 用于处理特殊字符，使其在正则表达式中被视为普通字符
  bad_patterns = '|'.join(re.escape(bad) for bad in bad_list)
  # 使用 re.split 将文章按 bad 列表中的片段分割
  parts = re.split(f'({bad_patterns})', essay)
  result = []
  current_id = -1
  for part in parts:
    if part in bad_map:
      # 如果分割出的部分在 bad_list 中，则使用相应的 ID
      current_id = bad_map[part]
    else:
      # 否则，将 ID 设置为 -1
      current_id = -1
    result.append({'id': current_id, 'val': part})
  return result

class AnalyzeEssayView(LoginRequiredMixin, View):
  def get(self, request):
    form = EssayForm()
    sub = Subscription.objects.get(user=request.user)
    return render(request, 'check.html', {'form': form, 'sub': sub})

  def post(self, request):
    sub = Subscription.objects.get(user=request.user)
    if not sub.is_subscribed and sub.credits == 0 and request.user.email != 'rayjoo333@gmail.com':
      messages.error(request, 'You have already tried twice. Please subscribe to continue!')
      return render(request, 'check.html', {'form': form, 'sub': sub})
    form = EssayForm(request.POST)
    if form.is_valid():
      topic = form.cleaned_data['topic']
      essay = form.cleaned_data['essay']
      count = form.cleaned_data['word_count']

      completion = chatCompletions("Topic: {} Essay: {}".format(topic, essay))
      result = json.loads(completion.choices[0].message.content)
      if 'error' in result:
        messages.error(request, result['error'])
        return render(request, 'check.html', {'form': form, 'sub': sub})
      result['splits'] = splitEssay(essay, [item['bad'] for item in result['explanations']])
      result['count'] = count
      result['topic'] = topic
      result['essay'] = essay
      sub.use()
      return render(request, 'analysis.html', { 'result': result })
    else:
      return render(request, 'check.html', {'form': form, 'sub': sub})

@require_POST
def export_pdf(request):
  result_str = request.POST.get('result', '')
  result = json.loads(result_str)

  # 渲染 HTML 模板
  html_string = render_to_string('pdftmpl.html', {
    'result': {
      'overall': result['overall'],
      'explanations': result['explanations'],
      'count': result['count'],
    }
  })
  # 创建 HTTP 响应
  response = HttpResponse(html_string, content_type='text/html')
  response['Content-Disposition'] = 'attachment; filename="analysis_report.html"'
  return response

def home(request):
  return render(request, 'home.html', { 'result': EXAMPLE })
