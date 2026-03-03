import {
  ChangeDetectionStrategy,
  Component,
  input,
  output,
  computed,
  forwardRef,
} from '@angular/core';
import { NG_VALUE_ACCESSOR, ControlValueAccessor } from '@angular/forms';

@Component({
  selector: 'ui-input',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => InputComponent),
      multi: true,
    },
  ],
  template: `
    <input
      [type]="type()"
      [placeholder]="placeholder()"
      [disabled]="disabled()"
      [class]="classes()"
      (input)="onInput($event)"
      (blur)="onTouched()"
    />
  `,
})
export class InputComponent implements ControlValueAccessor {
  type = input<string>('text');
  placeholder = input<string>('');
  disabled = input<boolean>(false);
  class = input<string>('');

  valueChange = output<string>();

  private onChange = (_: unknown) => {};
  onTouched = () => {};

  classes = computed(() => {
    const base =
      'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50';
    return [base, this.class()].filter(Boolean).join(' ');
  });

  onInput(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    this.onChange(value);
    this.valueChange.emit(value);
  }

  writeValue(value: string): void {}
  registerOnChange(fn: (_: unknown) => void): void { this.onChange = fn; }
  registerOnTouched(fn: () => void): void { this.onTouched = fn; }
  setDisabledState(_: boolean): void {}
}
