import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi, bookingApi } from '../services/api';
import { Calendar, Clock, MapPin, Users, Euro, ArrowLeft, ArrowRight } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const spotLabels = {
  sylt: 'Sylt',
  romo: 'Rømø'
};

export default function BookingFlow() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  
  const [course, setCourse] = useState(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [bookingLoading, setBookingLoading] = useState(false);

  // Booking form data
  const [bookingData, setBookingData] = useState({
    course_id: courseId,
    booking_date: '',
    time_slot: { start_time: '', end_time: '' },
    spot: '',
    number_of_students: 1,
    student_names: [''],
    student_details: {},
    notes: ''
  });

  const [availability, setAvailability] = useState(null);
  const [availabilityLoading, setAvailabilityLoading] = useState(false);

  useEffect(() => {
    loadCourse();
  }, [courseId]);

  const loadCourse = async () => {
    try {
      setLoading(true);
      const courseData = await courseApi.getById(courseId);
      setCourse(courseData);
      setBookingData(prev => ({ 
        ...prev, 
        course_id: courseData.id,
        spot: courseData.spots[0] // Default to first available spot
      }));
    } catch (error) {
      console.error('Failed to load course:', error);
      setError('Course not found.');
    } finally {
      setLoading(false);
    }
  };

  const checkAvailability = async () => {
    if (!bookingData.booking_date || !bookingData.spot) return;

    try {
      setAvailabilityLoading(true);
      const availabilityData = await bookingApi.checkAvailability({
        course_id: courseId,
        booking_date: bookingData.booking_date,
        spot: bookingData.spot,
        number_of_students: bookingData.number_of_students
      });
      setAvailability(availabilityData);
    } catch (error) {
      console.error('Failed to check availability:', error);
      setError('Failed to check availability. Please try again.');
    } finally {
      setAvailabilityLoading(false);
    }
  };

  useEffect(() => {
    if (bookingData.booking_date && bookingData.spot) {
      checkAvailability();
    }
  }, [bookingData.booking_date, bookingData.spot, bookingData.number_of_students]);

  const handleTimeSlotSelect = (slot) => {
    setBookingData(prev => ({
      ...prev,
      time_slot: {
        start_time: slot.time_slot.start_time,
        end_time: slot.time_slot.end_time
      }
    }));
    setCurrentStep(3);
  };

  const handleStudentNamesChange = (index, value) => {
    const newNames = [...bookingData.student_names];
    newNames[index] = value;
    setBookingData(prev => ({
      ...prev,
      student_names: newNames
    }));
  };

  const handleNumberOfStudentsChange = (num) => {
    const newNames = Array(num).fill('').map((_, i) => 
      bookingData.student_names[i] || ''
    );
    setBookingData(prev => ({
      ...prev,
      number_of_students: num,
      student_names: newNames
    }));
  };

  const createBooking = async () => {
    try {
      setBookingLoading(true);
      setError('');

      const booking = await bookingApi.create(bookingData);
      
      // Redirect to payment
      navigate(`/booking/${booking.id}/payment`);
    } catch (error) {
      console.error('Failed to create booking:', error);
      setError(error.response?.data?.detail || 'Failed to create booking. Please try again.');
    } finally {
      setBookingLoading(false);
    }
  };

  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 30); // 30 days from now
    return maxDate.toISOString().split('T')[0];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!course) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">Course not found</h2>
        <button 
          onClick={() => navigate('/courses')}
          className="mt-4 inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Courses
        </button>
      </div>
    );
  }

  const steps = [
    { number: 1, title: 'Select Date & Location' },
    { number: 2, title: 'Choose Time Slot' },
    { number: 3, title: 'Student Details' },
    { number: 4, title: 'Review & Book' }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back Button */}
      <button 
        onClick={() => navigate('/courses')}
        className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="h-4 w-4 mr-1" />
        Back to Courses
      </button>

      {/* Course Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{course.name}</h1>
        <p className="text-gray-600 mb-4">{course.description}</p>
        
        <div className="flex flex-wrap gap-4 text-sm text-gray-500">
          <div className="flex items-center">
            <Clock className="h-4 w-4 mr-1" />
            {course.duration_hours}h session
          </div>
          <div className="flex items-center">
            <Users className="h-4 w-4 mr-1" />
            Max {course.max_students} students
          </div>
          <div className="flex items-center">
            <Euro className="h-4 w-4 mr-1" />
            {course.base_price} per person
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.number} className="flex items-center">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                currentStep >= step.number 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {step.number}
              </div>
              <span className={`ml-2 text-sm font-medium ${
                currentStep >= step.number ? 'text-blue-600' : 'text-gray-500'
              }`}>
                {step.title}
              </span>
              {index < steps.length - 1 && (
                <ArrowRight className="h-4 w-4 mx-4 text-gray-400" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {/* Step 1: Date & Location Selection */}
      {currentStep === 1 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
          <h2 className="text-lg font-semibold text-gray-900">Select Date & Location</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date
              </label>
              <input
                type="date"
                value={bookingData.booking_date}
                onChange={(e) => setBookingData(prev => ({ ...prev, booking_date: e.target.value }))}
                min={getMinDate()}
                max={getMaxDate()}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <select
                value={bookingData.spot}
                onChange={(e) => setBookingData(prev => ({ ...prev, spot: e.target.value }))}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                {course.spots.map(spot => (
                  <option key={spot} value={spot}>
                    {spotLabels[spot]}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Students
              </label>
              <select
                value={bookingData.number_of_students}
                onChange={(e) => handleNumberOfStudentsChange(parseInt(e.target.value))}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                {Array.from({ length: course.max_students }, (_, i) => i + 1).map(num => (
                  <option key={num} value={num}>
                    {num} Student{num > 1 ? 's' : ''}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => setCurrentStep(2)}
              disabled={!bookingData.booking_date || !bookingData.spot}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next: Choose Time
              <ArrowRight className="h-4 w-4 ml-2" />
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Time Slot Selection */}
      {currentStep === 2 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Choose Time Slot</h2>
            <button
              onClick={() => setCurrentStep(1)}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              <ArrowLeft className="h-4 w-4 inline mr-1" />
              Back
            </button>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <p className="text-sm text-blue-800">
              <strong>Selected:</strong> {spotLabels[bookingData.spot]} on {new Date(bookingData.booking_date).toLocaleDateString()} 
              for {bookingData.number_of_students} student{bookingData.number_of_students > 1 ? 's' : ''}
            </p>
          </div>

          {availabilityLoading ? (
            <div className="flex items-center justify-center py-8">
              <LoadingSpinner />
            </div>
          ) : availability?.available ? (
            <div className="space-y-3">
              <p className="text-sm font-medium text-gray-700">
                Available Time Slots:
              </p>
              {availability.available_slots.map((slot, index) => (
                <div
                  key={index}
                  onClick={() => handleTimeSlotSelect(slot)}
                  className="p-4 border border-gray-200 rounded-md hover:border-blue-500 hover:bg-blue-50 cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">
                        {slot.time_slot.start_time} - {slot.time_slot.end_time}
                      </p>
                      <p className="text-sm text-gray-500">
                        Instructor: {slot.instructor_name}
                      </p>
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400" />
                  </div>
                </div>
              ))}
            </div>
          ) : availability && !availability.available ? (
            <div className="text-center py-8">
              <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Available Slots</h3>
              <p className="text-gray-500">
                No time slots are available for the selected date and location. 
                Please try a different date.
              </p>
            </div>
          ) : null}
        </div>
      )}

      {/* Step 3: Student Details */}
      {currentStep === 3 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Student Details</h2>
            <button
              onClick={() => setCurrentStep(2)}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              <ArrowLeft className="h-4 w-4 inline mr-1" />
              Back
            </button>
          </div>

          <div className="space-y-4">
            {bookingData.student_names.map((name, index) => (
              <div key={index}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Student {index + 1} Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => handleStudentNamesChange(index, e.target.value)}
                  placeholder="Enter full name"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            ))}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Additional Notes
              </label>
              <textarea
                value={bookingData.notes}
                onChange={(e) => setBookingData(prev => ({ ...prev, notes: e.target.value }))}
                placeholder="Any special requirements, experience level, or notes for the instructor..."
                rows={3}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => setCurrentStep(4)}
              disabled={bookingData.student_names.some(name => !name.trim())}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next: Review
              <ArrowRight className="h-4 w-4 ml-2" />
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Review & Book */}
      {currentStep === 4 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Review & Book</h2>
            <button
              onClick={() => setCurrentStep(3)}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              <ArrowLeft className="h-4 w-4 inline mr-1" />
              Back
            </button>
          </div>

          <div className="border border-gray-200 rounded-md p-4 space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Course:</span>
              <span className="font-medium">{course.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Date:</span>
              <span className="font-medium">{new Date(bookingData.booking_date).toLocaleDateString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Time:</span>
              <span className="font-medium">{bookingData.time_slot.start_time} - {bookingData.time_slot.end_time}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Location:</span>
              <span className="font-medium">{spotLabels[bookingData.spot]}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Students:</span>
              <div className="text-right">
                {bookingData.student_names.map((name, index) => (
                  <div key={index} className="font-medium">{name}</div>
                ))}
              </div>
            </div>
            {bookingData.notes && (
              <div className="flex justify-between">
                <span className="text-gray-600">Notes:</span>
                <span className="font-medium text-right max-w-xs">{bookingData.notes}</span>
              </div>
            )}
            <hr />
            <div className="flex justify-between text-lg font-bold">
              <span>Total Price:</span>
              <span>€{(course.base_price * bookingData.number_of_students).toFixed(2)}</span>
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <p className="text-sm text-yellow-800">
              <strong>Payment:</strong> A 30% deposit (€{((course.base_price * bookingData.number_of_students) * 0.3).toFixed(2)}) 
              will be required to confirm your booking. The remaining balance can be paid on the day of your lesson.
            </p>
          </div>

          <div className="flex justify-end">
            <button
              onClick={createBooking}
              disabled={bookingLoading}
              className="inline-flex items-center px-6 py-3 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {bookingLoading ? (
                <LoadingSpinner size="sm" className="mr-2" />
              ) : (
                <Euro className="h-5 w-5 mr-2" />
              )}
              {bookingLoading ? 'Creating Booking...' : 'Confirm & Pay Deposit'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}