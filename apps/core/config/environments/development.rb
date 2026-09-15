# development -- the behaviour profile you run while writing code.
#
# Rails-shaped, not Rails: stdlib only, same three names, same semantics.
# What matters here is that this is a BEHAVIOUR, not a place. You can run it
# on a laptop, on a shared box, or in a container, and it is the same
# environment in all three.
{
  "name"          => "development",
  "eager_load"    => false,
  "cache_classes" => false,
  "show_errors"   => true,     # full backtrace to the browser
  "log_level"     => "debug",
  "authorizing"   => false,    # a verdict from here means nothing about prod
}
