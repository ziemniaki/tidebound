# One supported save format. Historic demo migrations are intentionally retired.
module Tidebound
  class UnsupportedSave < StandardError
  end

  module SaveFormat
    module_function

    def validate!(data)
      state = data.is_a?(Hash) && data[:tidebound]
      return data if state.is_a?(State) && state.schema_version == SAVE_SCHEMA

      raise UnsupportedSave,
            "This save belongs to an unsupported Tidebound version. " \
              "Open it with its original game version, or start a new game. " \
              "The existing save file has not been changed."
    end
  end

  module SaveBoundary
    def read_from_file(path)
      # The stock reader runs historic conversions and may write the file back.
      # Validate before any conversion or write; this project accepts one schema.
      SaveFormat.validate!(get_data_from_file(path))
    end

    def load_all_values(data)
      SaveFormat.validate!(data)
      super
    end
  end
end
SaveData.singleton_class.prepend(Tidebound::SaveBoundary)
