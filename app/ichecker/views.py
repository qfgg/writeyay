import json
from django.shortcuts import render
from django.http import JsonResponse

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
  ]
}

mock = { "total": 5.5, "breakdown": { "ta": 5.5, "cc": 5.0, "lr": 5.5, "gra": 6.0 }, "summary": { "ta": "The essay addresses the task by discussing both attitudes of trying new things and sticking with familiar ones. However, the explanation is somewhat vague and lacks depth in examples and arguments. The conclusion does not clearly restate or support the writer's opinion effectively.", "cc": "The coherence and cohesion are somewhat weak. Ideas are not always logically connected, and transitions between points are abrupt. There are some issues with paragraphing, and the essay could benefit from clearer organization.", "lr": "The lexical resource is generally adequate but lacks variety. There are some word choices that are awkward or not quite appropriate, which affects the clarity and precision of the essay.", "gra": "Grammatical range and accuracy are generally good with some errors. Sentence structures are varied, but there are occasional mistakes in word choice and grammar that affect readability." },
"examples": [ { "bad": "travelling to many new refreshing places", "hint": "The word 'refreshing' is not appropriate in this context. Consider using 'exciting' or 'novel' to better describe new places." }, { "bad": "change the boring atmosphere that they need to witness every day", "hint": "The phrase is awkward. A clearer expression might be 'break the monotony of their daily routine.'" }, { "bad": "yearn to taste a bunch of different cuisines", "hint": "The phrase 'a bunch of' is informal. Use 'a variety of' instead." }, { "bad": "it also involves some shortcomings.The adaptations and the embarrassment", "hint": "There is a missing space after the period. Additionally, 'the adaptations and the embarrassment' is vague. Clarify what shortcomings are being referred to." }, { "bad": "first time going visitors", "hint": "The phrase should be 'first-time visitors' to indicate that it is their initial experience." }, { "bad": "choosing to carry out the ongoing familiar tasks helps everyone become stably developed", "hint": "The phrase 'stably developed' is awkward. Consider 'steadily progress' or 'develop consistently' instead." }, { "bad": "Compare to the more adventurous counterpart", "hint": "The correct phrase should be 'Compared to the more adventurous individuals'." }, { "bad": "staying in an old traditional place", "hint": "The phrase 'old traditional place' could be clearer. Consider 'sticking to familiar environments' for better clarity." }, { "bad": "it is better to make a lot of effort to pursue the things that belong to you", "hint": "The expression 'things that belong to you' is unclear. Consider 'pursue familiar interests and routines' for better coherence." } ]}

def analyze_essay(request):
    body = request.body
    data = json.loads(body)
    print(data)
    return JsonResponse(mock)

def home(request):
    return render(request, 'home.html', { 'result': EXAMPLE })
