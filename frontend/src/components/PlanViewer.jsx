function PlanViewer({ plan, onRefresh }) {
  if (!plan || !plan.steps || plan.steps.length === 0) {
    return (
      <div className="p-4 text-gray-400 text-sm">
        <p>No active plan</p>
        <button
          onClick={onRefresh}
          className="mt-2 text-blue-400 hover:text-blue-300"
        >
          Refresh
        </button>
      </div>
    )
  }

  // Normalize step format - handle both 'step'/'completed' and 'description'/'status' formats
  const normalizedSteps = plan.steps.map(s => ({
    description: s.description || s.step,
    status: s.status || (s.completed ? 'completed' : 'pending'),
    result: s.result
  }))

  const completedSteps = normalizedSteps.filter(step => step.status === 'completed').length
  const progress = (completedSteps / normalizedSteps.length) * 100

  return (
    <div className="p-4 overflow-y-auto h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-lg">Current Plan</h3>
        <button
          onClick={onRefresh}
          className="text-blue-400 hover:text-blue-300 text-sm"
        >
          Refresh
        </button>
      </div>

      {plan.task && (
        <p className="text-sm text-gray-300 mb-4"><strong>Task:</strong> {plan.task}</p>
      )}
      {plan.description && (
        <p className="text-sm text-gray-300 mb-4">{plan.description}</p>
      )}

      <div className="mb-4">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Progress</span>
          <span>{completedSteps}/{normalizedSteps.length} steps</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="space-y-2">
        {normalizedSteps.map((step, index) => (
          <div
            key={index}
            className={`p-3 rounded border ${
              step.status === 'completed'
                ? 'bg-green-900/20 border-green-700'
                : step.status === 'in_progress'
                ? 'bg-blue-900/20 border-blue-700'
                : 'bg-gray-800 border-gray-700'
            }`}
          >
            <div className="flex items-start gap-2">
              <span className="mt-1">
                {step.status === 'completed' ? '✓' :
                 step.status === 'in_progress' ? '⟳' : '○'}
              </span>
              <div className="flex-1">
                <p className="text-sm">{step.description}</p>
                {step.result && (
                  <p className="text-xs text-gray-400 mt-1">{step.result}</p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default PlanViewer
