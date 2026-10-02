# Check statically named Tidebound receivers against the composed game's API.
# This deliberately does not infer types of locals, returns or engine objects.
module ApiChecks
  module_function

  def constant(node, nesting)
    return unless node.is_a?(RubyVM::AbstractSyntaxTree::Node)
    case node.type
    when :CONST
      constant_name(node.children.first, nesting)
    when :COLON2
      parent, name = node.children
      return constant_name(name, nesting) unless parent
      owner = constant(parent, nesting)
      return unless owner.is_a?(Module)
      unless owner.const_defined?(name, false)
        # Never invoke a feature's const_missing hook while inspecting source.
        raise NameError.new("Unknown constant", name, receiver: owner)
      end
      owner.const_get(name, false)
    when :COLON3
      if Object.const_defined?(node.children.first, false)
        Object.const_get(node.children.first, false)
      end
    end
  end

  def owned?(owner)
    owner.is_a?(Module) && (owner.name == "Tidebound" || owner.name&.start_with?("Tidebound::"))
  end

  def constant_name(name, nesting)
    owner = (nesting + [Object]).find { |scope| scope.const_defined?(name, false) }
    owner&.const_get(name, false)
  end

  def errors(source, file)
    found = []
    visit(RubyVM::AbstractSyntaxTree.parse(source), [], nil, file, found)
    found
  end

  def visit(node, nesting, receiver, file, found)
    return unless node.is_a?(RubyVM::AbstractSyntaxTree::Node)
    children = node.children
    case node.type
    when :MODULE, :CLASS
      # Conditional engine hooks may not exist in this composition.
      begin
        owner = constant(children.first, nesting)
      rescue NameError
        return
      end
      return unless owner.is_a?(Module)
      visit(children.last, [owner, *nesting], owner, file, found)
      return
    when :DEFN
      name, body = children
      owner = nesting.first
      # Confirm the exact loaded singleton body, not merely a matching method name.
      target = owner if owner&.respond_to?(name, true) &&
        owner.method(name).source_location == [file, node.first_lineno]
      visit(body, nesting, target, file, found)
      return
    when :DEFS
      target, _name, body = children
      target = target.type == :SELF ? receiver : constant(target, nesting)
      visit(body, nesting, target, file, found)
      return
    when :SCLASS
      visit(children.last, nesting, nil, file, found)
      return
    when :LAMBDA
      children.each { |child| visit(child, nesting, nil, file, found) }
      return
    when :ITER
      call, body = children
      visit(call, nesting, receiver, file, found)
      # Any block-taking API can rebind self. Named module calls remain checkable.
      visit(body, nesting, nil, file, found)
      return
    when :CALL, :QCALL, :ATTRASGN
      target, method = children
      self_call = target.type == :SELF
      begin
        target = self_call ? receiver : constant(target, nesting)
        if owned?(target) && !target.respond_to?(method, self_call)
          found << "#{file}:#{node.first_lineno}: unknown API #{target.name}.#{method}"
        end
      rescue NameError => error
        # Ignore unresolved engine APIs; report missing constants beneath our namespace.
        if owned?(error.receiver)
          found << "#{file}:#{node.first_lineno}: unknown API owner #{error.receiver.name}::#{error.name}"
        end
      end
    end
    children.each { |child| visit(child, nesting, receiver, file, found) }
  end

  def check(source, file)
    found = errors(source, file)
    raise found.join("\n") unless found.empty?
  end
end
