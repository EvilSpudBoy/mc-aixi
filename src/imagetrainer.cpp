//
// Created by Michael Stevens on 3/15/23.
//

#include <cassert>
#include <sstream>

#include "imagetrainer.hpp"
#include "util.hpp"

// The ImageTrainer environment presents a random label each step.
// The agent's action is a predicted label; reward is 1 if correct.

ImageTrainer::ImageTrainer(options_t &options)
    : m_classes(4), m_max_steps(0), m_steps(0) {
    // Configure classes and an optional max step limit
    getOption(options, "image-classes", 4, m_classes);
    getOption(options, "image-max-steps", 0, m_max_steps);
    if (m_classes < 1) m_classes = 1;

    // Initial percept
    m_observation = randRange(m_classes); // class id in [0, m_classes)
    m_reward = 0;
}

void ImageTrainer::performAction(action_t action) {
    assert(isValidAction(action));
    m_action = action;

    // Sample the current label (observation) and compute reward
    m_observation = randRange(m_classes);
    m_reward = (action == m_observation) ? 1 : 0;

    // Step accounting
    ++m_steps;
}

bool ImageTrainer::isFinished(void) const {
    return (m_max_steps > 0) && (m_steps >= m_max_steps);
}

action_t ImageTrainer::maxAction() const { return m_classes - 1; }
percept_t ImageTrainer::maxObservation() const { return m_classes - 1; }
percept_t ImageTrainer::maxReward() const { return 1; }

std::string ImageTrainer::print() const {
    std::ostringstream out;
    out << "predicted: " << m_action
        << ", label: " << m_observation
        << ", reward: " << m_reward << std::endl;
    return out.str();
}
