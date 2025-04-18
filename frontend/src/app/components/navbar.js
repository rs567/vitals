import {
    Navbar,
    NavbarBrand,
    NavbarContent,
    NavbarItem,
    Link,
    Input,
    DropdownItem,
    DropdownTrigger,
    Dropdown,
    DropdownMenu,
    Avatar,
  } from "@heroui/react";

export const VitalsLogo = () => {
    return (
      <svg fill="none" height="36" viewBox="0 0 32 32" width="36">
        <path
          clipRule="evenodd"
          d="M17.6482 10.1305L15.8785 7.02583L7.02979 22.5499H10.5278L17.6482 10.1305ZM19.8798 14.0457L18.11 17.1983L19.394 19.4511H16.8453L15.1056 22.5499H24.7272L19.8798 14.0457Z"
          fill="currentColor"
          fillRule="evenodd"
        />
      </svg>
    );
};

export default function VitalsNavbar() {
    return (
        <Navbar isBordered
            classNames={{
                base: [
                    // "border-red-900",
                    // "border-b-8"
                ],
                item: [
                    "pl-2",
                    "pr-2",
                ]
            }}
        >
            <NavbarContent justify="start">
                <NavbarBrand className="mr-4">
                    <VitalsLogo />
                    <p className="hidden text-xl sm:block font-bold">Vitals</p>
                </NavbarBrand>
                <NavbarContent className="hidden sm:flex gap-3">
                    <NavbarItem>
                        <Link color="foreground" href="#">
                            <p className="text-xl hover:text-orange-400">Upload</p>
                        </Link>
                    </NavbarItem>
                    <NavbarItem isActive>
                        <Link aria-current="page" color="secondary" href="#">
                            <p className="text-xl hover:text-orange-400">Bills</p>
                        </Link>
                    </NavbarItem>
                    <NavbarItem>
                        <Link color="foreground" href="#">
                            <p className="text-xl hover:text-orange-400">Calendar</p>
                        </Link>
                    </NavbarItem>
                    <NavbarItem>
                        <Link color="foreground" href="#">
                            <p className="text-xl hover:text-orange-400">Medical Records</p>
                        </Link>
                    </NavbarItem>
                    <NavbarItem>
                        <Link color="foreground" href="#">
                            <p className="text-xl hover:text-orange-400">File Explorer</p>
                        </Link>
                    </NavbarItem>
                </NavbarContent>
            </NavbarContent>
        </Navbar>
    );
}