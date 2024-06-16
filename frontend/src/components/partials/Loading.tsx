const Loading = () => {
    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="flex flex-col items-center">
                <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-purple-600">
                    <img src="pedro.png" alt="pedro" className="w-full h-full object-cover animate-[spin_60s_linear_infinite]" />
                </div>
            </div>
        </div>
    );
};

export default Loading;