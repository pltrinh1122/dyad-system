judged: ready (source 6b6d2a387e4d2f0dca41ec6e7ebacbea406bc54086d9170e1644f7a0673cb9b8)
T0 [symptom; H] With many sessions running, I lose track of what each one is doing.
  observed: resumed × after a series: I come back to a row of windows and cannot say, for each, what it did, what it is doing, or whether it waits on me.
  T1 [cause; H] Each session tells its state only in its own window, so the state of all of them is held nowhere but in my memory.
    observed: during × after a series: to know where things stand I click through every window in turn.
    T1.1 [cause; H] Within one window, outcome, progress talk and what it needs from me run together, so even one session takes reading to understand.
      observed: resumed × after one prompt: a single reply is pages of narration with the result and a question somewhere inside.
      T1.1.1 [root-cause; H] Rebuilding where a session stands costs me a reread of its history each time I return, more than I can spend across many.
        removal test [H]: removed, T1.1 falls away and most of T1 and T4 with it; T0 shrinks to what T2 and T3 still cause.
    T1.2 [root-cause; H] The only map of which session is doing what is in my head, and it fades the moment I turn to another.
      removal test [H]: removed, T1 falls away, and with it the losses T2 and T3 cause through it (drift and overlap go unnoticed only because the map is mine alone); most of T0 falls away.
  T2 [cause; H] Sessions drift from what I asked: they widen scope, start sub-tasks and act on things I did not name.
    observed: during × after a series: a session started for one fix is editing files I never mentioned.
    T2.1 [cause; H] Each session reads my standing instructions its own way, and none shows which part of them it is acting under.
      observed: during × after one prompt: two sessions given the same rules take opposite actions on the same kind of case.
      T2.1.1 [root-cause; H] From what a session shows, I cannot tell whether what it is doing now is something I authorized or something it decided.
        removal test [H]: removed, T2.1 and T2 fall away (drift would show as departure the moment it starts), and the anchor branch's need to watch every session (T5.2) falls away with them.
    → T1.2
  T3 [cause; H] Sessions touch the same files, branches or outboxes without knowing of each other.
    observed: during × after a series: one session's change undoes another's, or two report done on overlapping work.
    T3.1 [cause; H] Nothing between sessions tells one what another holds; the overlap is visible only to me.
      observed: resumed × after a series: I find the collision only when I compare two windows by hand.
      → T1.2
  T4 [cause; H] Questions sessions put to me wait unseen in windows I am not looking at, so work stalls and I learn of it only on my return.
    observed: resumed × after one prompt: a session has waited hours on a yes I never saw.
    T4.1 [root-cause; H] I cannot tell which sessions are waiting on me and which are still working, so my attention goes to the wrong one.
      removal test [H]: removed, T4 falls away and part of T0 with it (stalled sessions no longer read as lost ones); T1.1 eases where the buried item was a question.
    → T1.1.1
  T5 [cause; H] Why must I keep track at all? Whatever any session edits, runs or sends is mine once it lands; I cannot disown it.
    observed: resumed × after a series: I am asked what changed today and must answer for every session, not just the one I watched.
    T5.1 [anchor; H] I answer for the result.
    T5.2 [cause; H] I would not need to watch every session if each could be trusted to stop and tell me when it departs from what I asked.
      observed: during × after a series: I keep glancing at quiet windows in case one has gone its own way.
      → T2.1.1
