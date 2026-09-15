# production -- the behaviour profile customers get.
#
# AND THE POINT OF THIS REPOSITORY: a staging HOST runs this ENVIRONMENT.
# That is not a workaround, it is the only way a staging verdict means
# anything. If staging ran `development`, every production-only path would be
# off and its pass would be a statement about a program customers never run.
#
# There is no `staging.rb`, deliberately. Adding one is the Rails footgun:
# Rails.env.production? goes false and the environment stops resembling the
# thing it exists to rehearse.
{
  "name"          => "production",
  "eager_load"    => true,
  "cache_classes" => true,
  "show_errors"   => false,    # a customer never sees a backtrace
  "log_level"     => "info",
  "authorizing"   => true,     # a verdict from HERE can authorize -- if the
                               # host is one we trust to stand in for prod
}
