Contributing
============

Guidelines For Reporting An Issue/Feature
-----------------------------------------

So you've found a bug or have a great idea for a feature. Here's the steps you
should take to help get it added/fixed in Borgia:

* First, check to see if there's an existing issue/pull request for the
  bug/feature. All issues are at <https://github.com/borgia-app/Borgia/issues>
  and pull reqs are at <https://github.com/borgia-app/Borgia/pulls.>
* If there isn't one there, please file an issue. The ideal report includes:
  + A description of the problem/suggestion.
  + How to recreate the bug.
  + If relevant, including the versions of your:
    - Python interpreter
    - Django
    - Borgia
    - Optionally of the other dependencies involved
  + IDEALLY, creating a pull request with a (failing) test case demonstrating
   what's wrong. This makes it easy for us to reproduce & fix the problem.

Guidelines For Contributing Code
--------------------------------

If you're ready to take the plunge & contribute back some code/docs, the
process should look like:

* Fork the project on GitHub into your own account.
* Clone your copy of Borgia.
* Make a new branch in git & commit your changes there.
* Push your new branch up to GitHub.
* Again, ensure there isn't already an issue or pull request out there on it.
  If there is & you feel you have a better fix, please take note of the issue
  number & mention it in your pull request.
* Create a new pull request (based on your branch), including what the
  problem/feature is, versions of your software & referencing any related
  issues/pull requests.

In order to be merged into Borgia, contributions must have the following:

* A solid patch that:
  + is clear.
  + works across all supported versions of Python/Django.
  + follows the existing style of the code base (mostly PEP-8).
  + comments included as needed to explain why the code functions as it does
* A test case that demonstrates the previous flaw that now passes
  with the included patch.

If your contribution lacks any of these things, they will have to be added
by a core contributor before being merged into Borgia properly, which may take
substantial time for the all-volunteer team to get to.