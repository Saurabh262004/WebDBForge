from Node import NodeEvaluator

node = {
  '__node__': 'create',
  'method': 'range',
  'kwargs': {'start': 0, 'end': 10, 'step': 2}
}

result = NodeEvaluator.eval(node)

print(result)  # Output: [0, 2, 4, 6, 8]
