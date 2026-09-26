$VERBOSE = nil
module System
  def self.data_directory
    "/"
  end
  def self.user_language
    "en"
  end
end
module MessageTypes
  def self.const_missing(n)
    n
  end
end
def pbGetMessageFromHash(kind, value)
  value
end
def pbGetMessage(kind, value)
  value.to_s
end
def _INTL(s, *args)
  args.each_with_index { |v, i| s = s.gsub("{#{i + 1}}", v.to_s) }
  s
end
def pbGetLanguage
  2
end
def nil_or_empty?(v)
  v.nil? || v.empty?
end
module MultipleForms
  def self.call(*args)
    nil
  end
end
