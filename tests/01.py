test = {
  'name': 'Check if project.py exists',
  'points': 0,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> assert "project.py" in os.listdir(".")
          """,
          'hidden': False,
          'locked': False
        }
      ],
      'scored': False,
      'setup': r"""
      >>> import os
      """,
      'teardown': '',
      'type': 'doctest'
    }
  ]
}
