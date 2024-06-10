import React, { useLayoutEffect, useState, RefObject } from 'react';

type Step = {
  title: string;
  description: string;
  highlight: string;
};

interface TutorialPopUpModalProps {
  steps: Step[];
  isOpen: boolean;
  onClose: () => void;
  currentStep: number;
  handleNextStep: () => void;
  handlePreviousStep: () => void;
  highlightRef: RefObject<HTMLElement>;
}

const TutorialPopUpModal: React.FC<TutorialPopUpModalProps> = ({
  steps,
  isOpen,
  onClose,
  currentStep,
  handleNextStep,
  handlePreviousStep,
  highlightRef,
}) => {
  const [highlightStyle, setHighlightStyle] = useState<React.CSSProperties>({});

  const calculateHighlightStyle = () => {
    if (highlightRef.current) {
      const rect = highlightRef.current.getBoundingClientRect();
      const style = window.getComputedStyle(highlightRef.current);
      const marginTop = parseFloat(style.marginTop);
      const marginLeft = parseFloat(style.marginLeft);
      const marginRight = parseFloat(style.marginRight);
      const marginBottom = parseFloat(style.marginBottom);

      setHighlightStyle({
        top: rect.top - marginTop,
        left: rect.left - marginLeft,
        width: rect.width + marginLeft + marginRight,
        height: rect.height + marginTop + marginBottom,
      });
    }
  };

  useLayoutEffect(() => {
    // Use a timeout to allow the element to be fully rendered before measuring
    const timer = setTimeout(calculateHighlightStyle, 100);

    // Recalculate on window resize
    window.addEventListener('resize', calculateHighlightStyle);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', calculateHighlightStyle);
    };
  }, [currentStep, highlightRef]);

  if (!isOpen) return null;

  const isFirstStep = steps[currentStep] === steps[0];
  const isLastStep = steps[currentStep] === steps[steps.length - 1];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">
      <div className="fixed inset-0 bg-black bg-opacity-50"></div>
      <div className="highlight" style={highlightStyle}></div>
      <div className="relative bg-nyanza p-6 rounded-lg shadow-lg w-11/12 md:w-1/2 lg:w-1/3 z-10 pointer-events-auto">
        <div className="flex justify-between">
          <h2 className="text-xl font-bold mb-4">{steps[currentStep].title}</h2>
          <button onClick={onClose} className="ml-auto self-start">
            <svg
              className="h-6 w-6 hover:bg-gray-300"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path stroke="currentColor" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <p className="mb-6">{steps[currentStep].description}</p>
        <div className={`flex ${!isFirstStep && !isLastStep ? 'justify-between' : ''} w-full`}>
          {!isFirstStep && (
            <button
              onClick={handlePreviousStep}
              disabled={isFirstStep}
              className="bg-spring-green px-4 py-2 rounded-lg"
            >
              Previous
            </button>
          )}
          {!isLastStep && (
            <button
              onClick={handleNextStep}
              disabled={isLastStep}
              className="bg-spring-green px-4 py-2 rounded-lg ml-auto"
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default TutorialPopUpModal;
