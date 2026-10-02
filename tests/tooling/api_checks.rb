# Synthetic API only: no quest, engine service or gameplay helper dependencies.
source = <<~RUBY
  module Tidebound
    module ApiFixture
      class << self
        attr_accessor :visible
        def hidden; end
        private :hidden
      end
      module_function
      def play
        return
      ensure
        self.removed = false
        Tidebound::ApiFixture.missing
        ApiFixture.missing
        self.visible = false
        self.hidden
        "Tidebound::ApiFixture.missing"
        unknown_dsl do
          self.rebound_receiver
          Tidebound::ApiFixture.missing_in_block
        end
        -> { self.rebound_lambda }
      end
      def self.other
        self.missing_singleton
      end
      # The instance method below is not the same body as this singleton method.
      def self.instance_only; end
      public
      def instance_only
        self.unknown_instance_receiver
      end
    end
  end
RUBY
eval(source, TOPLEVEL_BINDING, "api_fixture.rb")
expected = [
  "api_fixture.rb:12: unknown API Tidebound::ApiFixture.removed=",
  "api_fixture.rb:13: unknown API Tidebound::ApiFixture.missing",
  "api_fixture.rb:14: unknown API Tidebound::ApiFixture.missing",
  "api_fixture.rb:20: unknown API Tidebound::ApiFixture.missing_in_block",
  "api_fixture.rb:25: unknown API Tidebound::ApiFixture.missing_singleton"
]
unless ApiChecks.errors(source, "api_fixture.rb") == expected
  raise "API checker missed removed methods or misidentified a receiver"
end
Tidebound::ApiFixture.define_singleton_method(:const_missing) { |_name| raise "Executed hook" }
[
  ["Tidebound::MissingFeature.play", "unknown API owner Tidebound::MissingFeature"],
  ["Tidebound::ApiFixture::Missing.play", "unknown API owner Tidebound::ApiFixture::Missing"],
  ["Tidebound::ApiFixture.hidden", "unknown API Tidebound::ApiFixture.hidden"]
].each do |code, diagnostic|
  begin
    ApiChecks.check(code, "event.rb")
    raise "API checker accepted #{code}"
  rescue RuntimeError => error
    raise unless error.message == "event.rb:1: #{diagnostic}"
  end
end
Tidebound.send(:remove_const, :ApiFixture)
puts "PASS: API checks reject missing/private APIs and preserve unknown receiver boundaries."
