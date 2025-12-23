class NodeCreate:
  @staticmethod
  def nodeRange(start: int, end: int, step: int = 1) -> list[int]:
    return list(range(start, end, step))

NODE_METHODS = {
  'range': NodeCreate.nodeRange
}
