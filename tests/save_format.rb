# Save rejection precedes both in-memory loading and filesystem mutation.
new_opening
current = SaveData.compile_save_hash
roundtrip
check(Tidebound.state.schema_version == Tidebound::SAVE_SCHEMA, "current save schema lost")

[1, nil, Tidebound::SAVE_SCHEMA + 1].each do |version|
  old = Marshal.load(Marshal.dump(current))
  old[:tidebound].instance_variable_set(:@schema_version, version)
  before = [$player, $bag, $tidebound]
  begin
    SaveData.load_all_values(old)
    raise "unsupported save was accepted"
  rescue Tidebound::UnsupportedSave => error
    check(error.message.include?("has not been changed"), "save rejection lacks useful explanation")
  end
  check([$player, $bag, $tidebound] == before, "rejected save partially changed game globals")
end

# WASM does not mount the host filesystem. Model the native file-reader seam;
# the real native scenario checks disk contents separately.
module SaveData
  class << self
    alias native_get_data_from_file get_data_from_file
    def get_data_from_file(path)
      return $save_file_fixture if path == "fixture.rxdata"
      native_get_data_from_file(path)
    end
  end
end
$save_file_fixture = Marshal.load(Marshal.dump(current))
$save_file_fixture[:tidebound].instance_variable_set(:@schema_version, 1)
bytes = Marshal.dump($save_file_fixture)
begin
  SaveData.read_from_file("fixture.rxdata")
  raise "old disk save was accepted"
rescue Tidebound::UnsupportedSave
end
check(Marshal.dump($save_file_fixture) == bytes, "read converted an unsupported save")
$save_file_fixture = current
check(SaveData.read_from_file("fixture.rxdata") == current, "current disk save rejected")
puts "PASS: current saves round-trip; unsupported schemas are rejected before state or conversion changes."
