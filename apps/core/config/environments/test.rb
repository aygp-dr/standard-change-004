# test -- the behaviour profile a build is JUDGED in, not one it is placed in.
#
# This is the distinction the earlier builds never had a word for. `test` is
# not somewhere a build lives; it is somewhere a build is measured and then
# discarded. Rails has always had it and we never did -- our gate workflow
# stands up a real estate inside a CI runner and calls it neither an
# environment nor a host.
{
  "name"          => "test",
  "eager_load"    => false,
  "cache_classes" => true,     # deterministic: the suite must not see reloads
  "show_errors"   => true,
  "log_level"     => "warn",
  "authorizing"   => false,    # judged here, but not AUTHORIZED from here
}
